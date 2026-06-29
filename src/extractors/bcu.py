"""Real extractor for Uruguay's BCU exchange rate service.

Unlike BCP, BCU does not expose a REST/JSON endpoint: it publishes rates
through a SOAP/WSDL web service (`awsbcucotizaciones`), documented at
https://www.bcu.gub.uy/Acerca-de-BCU/RD_Solicitudes_Informacion/Documentaci%C3%B3n-Agregada/PedroScheeffer169.pdf

The `Execute` operation takes a structured `Entrada` (currency codes, a date
range capped at 31 days, and a currency group) and returns a `Salida` with a
`respuestastatus` block that must be checked before trusting the data:
Codigoerror 100 means "no quote for that date" (expected on weekends and
holidays); 101-107 mean bad input or the service being down.
"""
from datetime import date
from functools import lru_cache

from zeep import Client, Settings

WSDL_URL = "https://cotizaciones.bcu.gub.uy/wscotizaciones/servlet/awsbcucotizaciones?wsdl"

USD_CURRENCY_CODE = 2222
# Grupo 0 = "all groups". Confirmed against the live service that filtering
# by Grupo 2 ("Cotizaciones Locales", per the PDF) excludes USD entirely and
# always returns codigoerror 100; Moneda already narrows the result to USD.
GRUPO_TODOS = 0
CODIGOERROR_NO_QUOTE_FOR_DATE = 100


class BCUNoQuoteForDateError(Exception):
    """BCU has no published quote for the requested date (weekend/holiday)."""


class BCUServiceError(Exception):
    """BCU returned a non-OK `respuestastatus` other than 'no quote for date'."""


@lru_cache(maxsize=1)
def _client() -> Client:
    # BCU's response includes a placeholder `datoscotizaciones.dato` with a
    # blank Fecha even when codigoerror != 0; strict mode aborts the parse
    # on that empty date, so relax it to skip the bad field instead.
    return Client(wsdl=WSDL_URL, settings=Settings(strict=False))


def fetch_bcu_rate(rate_date: date) -> dict:
    """Fetches the USD/UYU quote for a single day via BCU's SOAP service."""
    response = _client().service.Execute(
        Entrada={
            "Moneda": [USD_CURRENCY_CODE],
            "FechaDesde": rate_date,
            "FechaHasta": rate_date,
            "Grupo": GRUPO_TODOS,
        }
    )

    status = response.respuestastatus
    if status.codigoerror == CODIGOERROR_NO_QUOTE_FOR_DATE:
        raise BCUNoQuoteForDateError(status.mensaje)
    if status.codigoerror != 0:
        raise BCUServiceError(f"BCU error {status.codigoerror}: {status.mensaje}")

    dato = response.datoscotizaciones["datoscotizaciones.dato"][0]
    return {
        "Fecha": dato.Fecha.isoformat(),
        "Moneda": dato.Moneda,
        "Nombre": dato.Nombre,
        "CodigoISO": dato.CodigoISO,
        "Emisor": dato.Emisor,
        "TCC": dato.TCC,
        "TCV": dato.TCV,
        "ArbAct": dato.ArbAct,
        "FormaArbitrar": dato.FormaArbitrar,
    }
