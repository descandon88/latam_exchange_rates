"""Data quality checks applied to normalized rate records before they are reported/loaded."""
from src.transforms.normalize import UNIFIED_FIELDS

REQUIRED_FIELDS = set(UNIFIED_FIELDS)


class ValidationError(Exception):
    pass


def validate_record(record: dict) -> None:
    missing = REQUIRED_FIELDS - record.keys()
    if missing:
        raise ValidationError(f"Record missing fields {missing}: {record}")
    if record["rate_buy"] <= 0 or record["rate_sell"] <= 0:
        raise ValidationError(f"Non-positive rate in record: {record}")
    if record["rate_sell"] < record["rate_buy"]:
        raise ValidationError(f"Sell rate lower than buy rate: {record}")


def validate_records(records: list) -> list:
    for record in records:
        validate_record(record)
    return records
