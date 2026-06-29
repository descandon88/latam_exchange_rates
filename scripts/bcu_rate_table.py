"""Print a table of USD/UYU rates from BCU's real SOAP service over a date range.

BCU caps a single Execute call at a 31-day range (codigoerror 104 if
exceeded); this prints whatever it returns without trying to page around it.

Usage: python scripts/bcu_rate_table.py 2025-03-01 2025-03-31
"""
import sys
from datetime import datetime

from src.extractors.bcu import CODIGOERROR_NO_QUOTE_FOR_DATE, GRUPO_TODOS, USD_CURRENCY_CODE, _client

if __name__ == "__main__":
    fecha_desde = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    fecha_hasta = datetime.strptime(sys.argv[2], "%Y-%m-%d").date()

    response = _client().service.Execute(
        Entrada={
            "Moneda": [USD_CURRENCY_CODE],
            "FechaDesde": fecha_desde,
            "FechaHasta": fecha_hasta,
            "Grupo": GRUPO_TODOS,
        }
    )

    status = response.respuestastatus
    if status.codigoerror == CODIGOERROR_NO_QUOTE_FOR_DATE:
        print(f"No quotes published between {fecha_desde} and {fecha_hasta}.")
    elif status.codigoerror != 0:
        print(f"BCU error {status.codigoerror}: {status.mensaje}")
    else:
        datos = response.datoscotizaciones["datoscotizaciones.dato"] or []
        print(f"{'Fecha':<12}{'TCC (compra)':<14}{'TCV (venta)':<14}")
        for dato in sorted(datos, key=lambda d: d.Fecha):
            print(f"{dato.Fecha.isoformat():<12}{dato.TCC:<14}{dato.TCV:<14}")
