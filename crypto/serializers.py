from rest_framework import serializers
from .models import CryptoPrice


class CryptoPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoPrice
        fields = [
            "id",
            "symbol",
            "name",
            "price_usd",
            "market_cap",
            "timestamp"
        ]
# Serializer = JSON schema + validation.
