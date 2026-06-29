from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src.extractors.bcu import (
    BCUNoQuoteForDateError,
    BCUServiceError,
    fetch_bcu_rate,
)


def _soap_response(codigoerror=0, mensaje="", dato=None):
    status = SimpleNamespace(codigoerror=codigoerror, mensaje=mensaje)
    datoscotizaciones = {"datoscotizaciones.dato": [dato] if dato else []}
    return SimpleNamespace(respuestastatus=status, datoscotizaciones=datoscotizaciones)


def test_fetch_bcu_rate_maps_soap_dato_to_raw_dict():
    dato = SimpleNamespace(
        Fecha=date(2026, 6, 26),
        Moneda=2222,
        Nombre="DOLAR USA",
        CodigoISO="USD",
        Emisor="ESTADOS UNIDOS",
        TCC=39.7,
        TCV=40.2,
        ArbAct=1.0,
        FormaArbitrar=0,
    )

    with patch("src.extractors.bcu._client") as mock_client:
        mock_client.return_value.service.Execute.return_value = _soap_response(dato=dato)
        raw = fetch_bcu_rate(date(2026, 6, 26))

    assert raw == {
        "Fecha": "2026-06-26",
        "Moneda": 2222,
        "Nombre": "DOLAR USA",
        "CodigoISO": "USD",
        "Emisor": "ESTADOS UNIDOS",
        "TCC": 39.7,
        "TCV": 40.2,
        "ArbAct": 1.0,
        "FormaArbitrar": 0,
    }


def test_fetch_bcu_rate_raises_no_quote_for_weekend_or_holiday():
    response = _soap_response(codigoerror=100, mensaje="No existe cotizacion para la fecha indicada")

    with patch("src.extractors.bcu._client") as mock_client:
        mock_client.return_value.service.Execute.return_value = response
        with pytest.raises(BCUNoQuoteForDateError):
            fetch_bcu_rate(date(2026, 6, 27))


def test_fetch_bcu_rate_raises_service_error_for_other_codes():
    response = _soap_response(codigoerror=107, mensaje="Servicio no disponible")

    with patch("src.extractors.bcu._client") as mock_client:
        mock_client.return_value.service.Execute.return_value = response
        with pytest.raises(BCUServiceError):
            fetch_bcu_rate(date(2026, 6, 27))
