import requests
import pandas as pd
from crypto.models import CryptoPrice
from django.utils import timezone


COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"


def fetch_and_store_crypto_prices():
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "sparkline": False
    }

    response = requests.get(COINGECKO_URL, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
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
