import os
import requests
import pandas as pd
from crypto.models import CryptoPrice
from django.utils import timezone


COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
# New: no key needed!
COINGECKO_LIST_URL = "https://api.coingecko.com/api/v3/coins/list"


class CoinGeckoCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # We still create attributes here (singleton init)
        return cls._instance

    def __init__(self):
        # This runs only once per singleton instance
        # Prevent re-init on subsequent calls
        if not hasattr(self, '_initialized'):
            self._coin_list = None
            self._symbol_to_id = {}
            self._name_to_id = {}
            self._initialized = True

    def load_mapping(self):
        if self._coin_list is not None:
            return

        try:
            resp = requests.get(COINGECKO_LIST_URL, timeout=15)
            resp.raise_for_status()
            self._coin_list = resp.json()

            for coin in self._coin_list:
                sym = coin['symbol'].lower()
                name_clean = coin['name'].lower().replace(
                    ' ', '-').replace('.', '').replace('(', '').replace(')', '')
                self._symbol_to_id[sym] = coin['id']
                self._name_to_id[name_clean] = coin['id']

            print(f"Loaded {len(self._coin_list)} coins from CoinGecko list")
        except Exception as e:
            print(f"Failed to load coin list: {e}")
            self._coin_list = []

    def get_coingecko_id(self, symbol: str, name: str = None) -> str | None:
        self.load_mapping()

        sym_lower = symbol.lower()
        if sym_lower in self._symbol_to_id:
            return self._symbol_to_id[sym_lower]

        if name:
            name_clean = (name.lower().replace(' ', '-').replace('.', '').
                          replace('(', '').replace(')', ''))

            if name_clean in self._name_to_id:
                return self._name_to_id[name_clean]

        print(f"No CoinGecko ID found for {symbol} ({name})")
        return None


# Singleton instance
coin_cache = CoinGeckoCache()


def fetch_and_store_crypto_prices():

    # Load from environment (fail early if missing)
    COINGECKO_API_KEY = os.environ.get('COINGECKO_API_KEY')

    if not COINGECKO_API_KEY:
        raise ValueError("Missing COINGECKO_API_KEY environment variable! "
                         "Add it in Render Dashboard > Environment variables.")
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "sparkline": False
        # Optional but useful: "locale": "en", "price_change_percentage": "24h"
    }

    headers = {
        "x-cg-demo-api-key": COINGECKO_API_KEY,  # ← Correct header name!
        "Accept": "application/json",            # Good practice
        # Helps avoid blocks
        "User-Agent": "crypto-backend/1.0 (u.qurreshi34@gmail.com)"
    }

    try:
        response = requests.get(COINGECKO_URL, params=params,
                                headers=headers, timeout=30)

        response.raise_for_status()

        data = response.json()

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print(
                "Rate limit hit (429) - Demo plan: ~30 calls/min. Wait a bit.")
        raise

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        raise

    df = pd.DataFrame(data)

    # 🔍 Keep only columns we care about
    # Returns a DataFrame with these columns
    # df['name']  # Returns a Series  (a single column as a 1D object)
    df = df[[
        "symbol",
        "name",
        "current_price",
        "market_cap"
    ]]

    # 🧹 Rename columns
    df = df.rename(columns={
        "current_price": "price_usd"
    })

    # pandas filtering examples
    df = df[df["price_usd"] > 1]  # remove dust coins
    # first 20 rows in the DataFrame as they currently exist
    # df = df.iloc[:20]
    # Sort all rows by price_usd (highest first) - Take the first 20 rows
    df = df.sort_values(by="price_usd", ascending=False).iloc[:20]

    # 🕒 Timestamp
    timestamp = timezone.now()

    # 🗑️ Clear old data
    CryptoPrice.objects.all().delete()

    # Save to DB
    # itertuples() is a pandas method that iterates over DataFrame rows as
    # named tuples - it's much faster than iterrows().
    # index=False: Excludes the row index from the tuple
    crypto_objects = []
    for row in df.itertuples(index=False):
        cg_id = coin_cache.get_coingecko_id(row.symbol, row.name)
        crypto_objects.append(
            CryptoPrice(
                symbol=row.symbol.upper(),
                name=row.name,
                price_usd=row.price_usd,
                market_cap=row.market_cap,
                timestamp=timestamp,
                coingecko_id=cg_id  # ← Save it!
            )
        )

    CryptoPrice.objects.bulk_create(crypto_objects)
