import pytest

from src.validation.checks import ValidationError, validate_record, validate_records

VALID_RECORD = {
    "source": "BCP",
    "country": "PY",
    "currency": "USD",
    "rate_date": "2026-06-27",
    "rate_buy": 7250.0,
    "rate_sell": 7300.0,
}


def test_validate_record_accepts_a_well_formed_record():
    validate_record(VALID_RECORD)  # does not raise


def test_validate_record_rejects_missing_fields():
    record = {k: v for k, v in VALID_RECORD.items() if k != "rate_date"}

    with pytest.raises(ValidationError):
        validate_record(record)


def test_validate_record_rejects_non_positive_rate():
    record = {**VALID_RECORD, "rate_buy": 0}

    with pytest.raises(ValidationError):
        validate_record(record)


def test_validate_record_rejects_sell_below_buy():
    record = {**VALID_RECORD, "rate_buy": 7300.0, "rate_sell": 7250.0}

    with pytest.raises(ValidationError):
        validate_record(record)


def test_validate_records_checks_every_item():
    with pytest.raises(ValidationError):
        validate_records([VALID_RECORD, {**VALID_RECORD, "rate_buy": -1}])
