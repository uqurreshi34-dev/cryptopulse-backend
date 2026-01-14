from django.core.management.base import BaseCommand
from crypto.services.coingecko import fetch_and_store_crypto_prices


class Command(BaseCommand):
    help = "Fetch crypto prices from CoinGecko and store them in the database"

    def handle(self, *args, **options):
        self.stdout.write("Fetching crypto prices...")

        fetch_and_store_crypto_prices()

        self.stdout.write(
            self.style.SUCCESS(
                "Crypto prices successfully fetched and stored.")
        )


# class Command(BaseCommand):
# ➡️ This is how Django knows: “This file defines a command.”
# help = "..."
# ➡️ Shows when you run python manage.py help
# def handle(self, *args, **options):
# ➡️ This is what runs when you call the command
# fetch_and_store_crypto_prices()
# ➡️ Calls your existing pandas + Neon logic
# ➡️ No duplication
# ➡️ No rewrite
