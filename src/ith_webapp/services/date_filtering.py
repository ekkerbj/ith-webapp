from datetime import date, datetime

from sqlalchemy import extract


def _as_date(value: date | datetime | str | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise TypeError(f"Unsupported date value: {type(value)!r}")


def month_compare(value: date | datetime | str | None, reference: date | datetime | str | None = None) -> bool:
    value_date = _as_date(value)
    if value_date is None:
        return False
    reference_date = _as_date(reference) if reference is not None else date.today()
    return value_date.month == reference_date.month and value_date.year == reference_date.year


def current_month_filter(column, reference: date | datetime | str | None = None):
    reference_date = _as_date(reference) if reference is not None else date.today()
    return (extract("month", column) == reference_date.month) & (
        extract("year", column) == reference_date.year
    )
