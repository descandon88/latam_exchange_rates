"""Normalizes each bank's raw schema into the unified rate record shape
stored in `exchange_rates.rates`.
"""

UNIFIED_FIELDS = ("source", "country", "currency", "rate_date", "rate_buy", "rate_sell")


def normalize_bcp(raw: dict) -> dict:
    return {
        "source": "BCP",
        "country": "PY",
        "currency": raw["moneda"],
        "rate_date": raw["fecha"],
        "rate_buy": float(raw["compra"]),
        "rate_sell": float(raw["venta"]),
    }


def normalize_bcu(raw: dict) -> dict:
    return {
        "source": "BCU",
        "country": "UY",
        "currency": raw["CodigoISO"],
        "rate_date": raw["Fecha"],
        "rate_buy": float(raw["TCC"]),
        "rate_sell": float(raw["TCV"]),
    }
