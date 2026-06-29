"""One-off diagnostic: ask BCU for every currency/group on one date.

`fetch_bcu_rate` got a 100 ("no existe cotizacion para la fecha indicada")
for every date tried with Moneda=[2222]/Grupo=2, including known-past business
days. Before trusting the USD code (2222) and group (2) taken from the PDF's
illustrative example, this dumps the raw `Moneda`/`Nombre`/`CodigoISO` BCU
actually returns for Moneda=[0] (all currencies) and Grupo=0 (all groups), so
we can confirm the real code/group pairing instead of guessing from the doc.

Usage: python scripts/discover_bcu_currencies.py 2025-03-10
"""
import sys
from datetime import datetime

from src.extractors.bcu import _client

if __name__ == "__main__":
    rate_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()

    response = _client().service.Execute(
        Entrada={
            "Moneda": [0],
            "FechaDesde": rate_date,
            "FechaHasta": rate_date,
            "Grupo": 0,
        }
    )

    status = response.respuestastatus
    print(f"status={status.status} codigoerror={status.codigoerror} mensaje={status.mensaje!r}")

    datos = response.datoscotizaciones["datoscotizaciones.dato"] or []
    print(f"{len(datos)} records for {rate_date}")
    for dato in datos:
        if dato.CodigoISO and "USD" in dato.CodigoISO.upper() or (dato.Nombre and "DOLAR" in dato.Nombre.upper()):
            print(f"  Moneda={dato.Moneda} Nombre={dato.Nombre!r} CodigoISO={dato.CodigoISO!r} "
                  f"Emisor={dato.Emisor!r} TCC={dato.TCC} TCV={dato.TCV}")
