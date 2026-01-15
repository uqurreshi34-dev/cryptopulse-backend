from django.db import models
from django.utils.timezone import now
# Create your models here.


class CryptoPrice(models.Model):
    symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    price_usd = models.DecimalField(max_digits=15, decimal_places=2)
    market_cap = models.BigIntegerField()
    timestamp = models.DateTimeField()
    # New field - can be null for coins we can't map
    coingecko_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.symbol} - {self.price_usd}"

# obviously initially, there will be no last_updated, so if
# we leave DateTimeField() like so, we'll get integrity error for null value
# we're saying “If no refresh has ever happened, treat it as ‘now’


class DataRefreshStatus(models.Model):
    last_updated = models.DateTimeField(default=now)

    def __str__(self):
        return f"Last refresh: {self.last_updated}"
