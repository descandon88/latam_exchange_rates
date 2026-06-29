"""Phase 1 stand-ins for the real BCP/BCU API clients.

Each function mimics the actual raw response shape of its bank so the
downstream normalize step has real work to do. They will be replaced by
real `requests` calls in Phase 2 without touching anything downstream.
"""
from datetime import date


def fetch_bcp_rate(rate_date: date) -> dict:
    """Mimics Paraguay's BCP daily USD rate response (buy/sell spread, Spanish field names)."""
    drift = (rate_date.timetuple().tm_yday % 10) * 5
    return {
        "fecha": rate_date.strftime("%Y-%m-%d"),
        "moneda": "USD",
        "compra": 7250.0 + drift,
        "venta": 7300.0 + drift,
    }


def fetch_bcu_rate(rate_date: date) -> dict:
    """Mimics one `datoscotizaciones.dato` record from BCU's real SOAP service
    (awsbcucotizaciones): a buy/sell spread (TCC/TCV), not a single rate.
    """
    drift = (rate_date.timetuple().tm_yday % 10) * 0.03
    buy = round(39.70 + drift, 2)
    return {
        "Fecha": rate_date.isoformat(),
        "Moneda": 2222,
        "Nombre": "DOLAR USA",
        "CodigoISO": "USD",
        "Emisor": "ESTADOS UNIDOS",
        "TCC": buy,
        "TCV": round(buy + 0.5, 2),
        "ArbAct": 1.0,
        "FormaArbitrar": 0,
    }
