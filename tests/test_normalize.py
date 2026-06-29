from src.transforms.normalize import normalize_bcp, normalize_bcu


def test_normalize_bcp_maps_spanish_fields_to_unified_schema():
    raw = {"fecha": "2026-06-27", "moneda": "USD", "compra": 7250.5, "venta": 7300.25}

    record = normalize_bcp(raw)

    assert record == {
        "source": "BCP",
        "country": "PY",
        "currency": "USD",
        "rate_date": "2026-06-27",
        "rate_buy": 7250.5,
        "rate_sell": 7300.25,
    }


def test_normalize_bcu_maps_tcc_tcv_to_buy_sell():
    raw = {
        "Fecha": "2026-06-27",
        "Moneda": 2222,
        "Nombre": "DOLAR USA",
        "CodigoISO": "USD",
        "Emisor": "ESTADOS UNIDOS",
        "TCC": 39.70,
        "TCV": 40.20,
        "ArbAct": 1.0,
        "FormaArbitrar": 0,
    }

    record = normalize_bcu(raw)

    assert record == {
        "source": "BCU",
        "country": "UY",
        "currency": "USD",
        "rate_date": "2026-06-27",
        "rate_buy": 39.70,
        "rate_sell": 40.20,
    }
