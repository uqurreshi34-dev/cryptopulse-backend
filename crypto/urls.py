from django.urls import path
from .views import (CryptoPriceListView, CryptoPriceDetailView,
                    refresh_status_view)

urlpatterns = [
    # Specific routes must come BEFORE dynamic routes
    # utility / metadata endpoints FIRST
    path("refresh-status/", refresh_status_view),

    # data endpoints
    path("prices/", CryptoPriceListView.as_view(), name="crypto-prices"),
    path("<str:symbol>/",
         CryptoPriceDetailView.as_view(), name="crypto-price-detail"),
]
