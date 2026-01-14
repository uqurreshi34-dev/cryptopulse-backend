from django.contrib import admin
from .models import CryptoPrice

# Register your models here.


@admin.register(CryptoPrice)
class CryptoPriceAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'price_usd', 'timestamp')
