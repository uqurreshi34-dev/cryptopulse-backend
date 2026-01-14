from django.urls import path
from .views import CryptoPriceListView, CryptoPriceDetailView

urlpatterns = [
    path("prices/", CryptoPriceListView.as_view(), name="crypto-prices"),
    path("<str:symbol>/",
         CryptoPriceDetailView.as_view(), name="crypto-price-detail")
]
