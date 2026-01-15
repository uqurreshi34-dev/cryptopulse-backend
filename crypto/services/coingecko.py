import os
import requests
import pandas as pd
from crypto.models import CryptoPrice
from django.utils import timezone


COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
# Load from environment (fail early if missing)
COINGECKO_API_KEY = os.environ.get('COINGECKO_API_KEY')

if not COINGECKO_API_KEY:
    raise ValueError("Missing COINGECKO_API_KEY environment variable! "
                     "Add it in Render Dashboard > Environment variables.")


def fetch_and_store_crypto_prices():
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
        crypto_objects.append(
            CryptoPrice(
                symbol=row.symbol.upper(),
                name=row.name,
                price_usd=row.price_usd,
                market_cap=row.market_cap,
                timestamp=timestamp
            )
        )

    CryptoPrice.objects.bulk_create(crypto_objects)
