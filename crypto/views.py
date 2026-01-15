from django.http import Http404
from rest_framework.generics import ListAPIView, RetrieveAPIView
from crypto.services.price_refresher import refresh_prices_if_stale
from .models import CryptoPrice
from .serializers import CryptoPriceSerializer
from django.http import JsonResponse
from crypto.models import DataRefreshStatus

# ListAPIView - Get multiple objects (a list)
# RetrieveAPIView - Get a single specific object
#  def get_queryset(self) and def get_object(self) called automatically
# in RetrieveAPIView and ListAPIView
# Create your views here. (class based views in this example)


class CryptoPriceListView(ListAPIView):
    serializer_class = CryptoPriceSerializer

    def get_queryset(self):  # called automatically -> useful for refresh
        refresh_prices_if_stale()  # refresh
        return CryptoPrice.objects.all().order_by("-market_cap")

# queryset and serializer_class are the 2 most fundamental
# class attributes you will use when working with ListAPIView
# queryset tells the view which db records it should retrieve
# serializer_class tells the view which serializer to use to convert
# those db records into JSON format (NOT USING queryset anymore!)

# Why ListAPIView?

# Read-only

# Pagination-ready

# Clean & simple

# Very common in production

#  — prefix indicates request is intentionally unused - no yellow squiggly


class CryptoPriceDetailView(RetrieveAPIView):
    serializer_class = CryptoPriceSerializer
    # lookup_field is a built-in attribute in Django REST Framework's
    # generic views (like RetrieveAPIView, UpdateAPIView, DestroyAPIView
    # lookup_field = "symbol"

    def get_queryset(self):
        refresh_prices_if_stale()
        return CryptoPrice.objects.all()

    def get_object(self):  # e.g. self.kwargs = {'symbol': 'BTC'}
        symbol = self.kwargs.get("symbol")

        try:
            return self.get_queryset().filter(
                symbol__iexact=symbol
            ).latest("timestamp")
        except CryptoPrice.DoesNotExist as exc:
            raise Http404("Crypto symbol not found.") from exc

# _request means: “this argument is required but intentionally unused”
# Django always sends a request object even if we dont use it
# The below is a function based view


def refresh_status_view(_request):
    status = DataRefreshStatus.objects.first()

    return JsonResponse({
        "last_updated": status.last_updated.isoformat() if status else None
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

# Yes, get_queryset() gets called automatically by Django's
# generic views (like ListView, DetailView, etc.) when they need to fetch data.
# When it's called:

# When the view renders the page
# Each time the view needs to access the queryset
# Before applying any filtering, pagination, or ordering

# Example:
# pythonclass CryptoPriceListView(ListView):
#     model = CryptoPrice

#     def get_queryset(self):
#         refresh_prices_if_stale()  # This runs automatically
#         return CryptoPrice.objects.all()
# When someone visits the URL mapped to this view, Django automatically
# calls get_queryset() to fetch the data.
# Key points:

# You don't call it yourself in your code
# Django's generic views call it internally
# It's a hook/override point where you can customize the queryset
# It runs on every request to that view

# If you're NOT using a generic view (like if you have a plain
# function-based view), then get_queryset() wouldn't be called
# automatically—you'd need to call methods manually.


# Situation	Needs self?
# Function-based view	❌ No
# Class-based view method	✅ Yes
# Django always passes request	✅ Yes
