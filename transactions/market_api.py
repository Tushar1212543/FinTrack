import requests
from decimal import Decimal
from django.conf import settings
from django.core.cache import cache


def get_current_price(symbol):

    symbol = symbol.strip().upper()

    # -------------------------
    # Check cached price
    # -------------------------

    cache_key = f"stock_price_{symbol}"

    cached_price = cache.get(cache_key)

    if cached_price is not None:
        return Decimal(str(cached_price))

    # -------------------------
    # Fetch price from IndianAPI
    # -------------------------

    response = requests.get(
        "https://stock.indianapi.in/stock",
        headers={
            "X-API-Key": settings.INDIAN_API_KEY
        },
        params={
            "name": symbol
        },
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    nse_price = data.get(
        "currentPrice",
        {}
    ).get("NSE")

    if nse_price is None:
        raise ValueError(
            f"NSE price not found for {symbol}"
        )

    price = Decimal(str(nse_price))

    # -------------------------
    # Store price in cache
    # -------------------------

    cache.set(
        cache_key,
        str(price),
        timeout=300
    )

    return price