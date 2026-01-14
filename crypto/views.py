from django.http import Http404
from django.views import View
from django.http import JsonResponse
from rest_framework.generics import ListAPIView
from .models import CryptoPrice
from .serializers import CryptoPriceSerializer


# Create your views here.

class CryptoPriceListView(ListAPIView):
    queryset = CryptoPrice.objects.all().order_by("-market_cap")
    serializer_class = CryptoPriceSerializer

# queryset and serializer_class are the 2 most fundamental
# class attributes you will use when working with ListAPIView
# queryset tells the view which db records it should retrieve
# serializer_class tells the view which serializer to use to convert
# those db records into JSON format

# Why ListAPIView?

# Read-only

# Pagination-ready

# Clean & simple

# Very common in production

#  — prefix indicates request is intentionally unused - no yellow squiggly


class CryptoPriceDetailView(View):
    def get(self, _request, symbol):
        try:
            crypto = CryptoPrice.objects.filter(
                symbol__iexact=symbol
            ).latest("timestamp")
        except CryptoPrice.DoesNotExist as exc:
            raise Http404("Crypto symbol not found.") from exc

        return JsonResponse({
            "id": crypto.id,
            "name": crypto.name,
            "symbol": crypto.symbol,
            "price_usd": float(crypto.price_usd),
            "market_cap": float(crypto.market_cap),
            "timestamp": crypto.timestamp.isoformat(),
        })


# symbol__iexact is built-in Django ORM syntax for case-insensitive
# exact matching!
# Django Field Lookups
# The double underscore __ is Django's way of specifying field lookups.
# The pattern is:
# pythonfield__lookup_type
# Common lookup types:
# python# Exact match (case-sensitive)
# CryptoPrice.objects.filter(symbol__exact="BTC")
# # or simply:
# CryptoPrice.objects.filter(symbol="BTC")

# # Case-insensitive exact match
# CryptoPrice.objects.filter(symbol__iexact="btc")
# # matches "BTC", "btc", "Btc"

# # Contains (case-sensitive)
# CryptoPrice.objects.filter(name__contains="Bit")

# # Case-insensitive contains
# CryptoPrice.objects.filter(name__icontains="bit")
# # matches "Bitcoin", "BITCOIN"

# # Starts with
# CryptoPrice.objects.filter(symbol__startswith="BT")

# # Case-insensitive starts with
# CryptoPrice.objects.filter(symbol__istartswith="bt")

# # Greater than
# CryptoPrice.objects.filter(price_usd__gt=1000)

# # Less than or equal
# CryptoPrice.objects.filter(price_usd__lte=5000)

# # In a list
# CryptoPrice.objects.filter(symbol__in=["BTC", "ETH", "DOGE"])
# Why iexact is perfect for your use case:
# python# User requests: /api/crypto/btc
# # Your code: symbol__iexact=symbol

# # This matches ANY of these in your database:
# # "BTC", "btc", "Btc", "bTC" → all return the same crypto
# This is great for URLs because users might type /crypto/bitcoin,
# /crypto/BITCOIN, or /crypto/Bitcoin and they'll all work!
# The i prefix means "case-insensitive":

# exact → case-sensitive
# iexact → case-insensitive
# contains → case-sensitive
# icontains → case-insensitive
# startswith → case-sensitive
# istartswith → case-insensitive

# So yes, it's 100% built-in Django magic! The double underscore is
# how Django does all its query filtering.
