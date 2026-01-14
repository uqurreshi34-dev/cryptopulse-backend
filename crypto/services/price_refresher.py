from datetime import timedelta

from django.utils.timezone import now

from crypto.models import DataRefreshStatus
from crypto.services.coingecko import fetch_and_store_crypto_prices

STALE_AFTER = timedelta(minutes=5)


def refresh_prices_if_stale():
    status, _ = DataRefreshStatus.objects.get_or_create(id=1)

    if now() - status.last_updated < STALE_AFTER:
        return False  # still fresh

    fetch_and_store_crypto_prices()

    status.last_updated = now()
    status.save()

    return True  # refreshed


# In Python (and Django), the ,_ is a way to unpack a tuple while
# ignoring one of the values.
# Let me break this down:
# DataRefreshStatus.objects.get_or_create(id=1) returns a tuple
# with two values:

# The object (either retrieved or created)
# A boolean indicating whether the object was created (True) or
# already existed (False)

# So when you write:
# pythonstatus, _ = DataRefreshStatus.objects.get_or_create(id=1)

# status gets the first value (the object)
# _ gets the second value (the boolean)

# The underscore _ is a Python convention meaning "I don't care
#  about this value." It's a valid variable name, but by convention
# it signals that you're intentionally ignoring that part of the return value.
# This is equivalent to:

# status, created = DataRefreshStatus.objects.get_or_create(id=1)
# But you never use the 'created' variable
# Using _ just makes it clearer that you're only interested in the object
# itself, not whether it was newly created or already existed.
