from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, time
from decimal import Decimal
import re
from typing import Any

from sqlalchemy import Boolean, Date, DateTime, Float, Integer, Numeric, Time
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.schema import MetaData, Table

REPLICATION_COLUMNS = frozenset(
    {"s_guid", "s_collineage", "s_generation", "s_lineage"}
)


def normalize_access_identifier(value: str) -> str:
    normalized = re.sub(r"[^0-9a-z]+", "_", value.casefold())
    return re.sub(r"_+", "_", normalized).strip("_")


def should_skip_access_column(column_name: str) -> bool:
    return normalize_access_identifier(column_name) in REPLICATION_COLUMNS


def migration_tables(metadata: MetaData) -> list[Table]:
    return list(metadata.sorted_tables)


def _source_lookup(source_row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        normalize_access_identifier(str(column_name)): value
        for column_name, value in source_row.items()
    }


def _parse_temporal_value(value: str, target_type: type[Any]) -> date | datetime | time:
    if target_type is datetime:
        return datetime.fromisoformat(value)
    if target_type is date:
        return date.fromisoformat(value)
    return time.fromisoformat(value)


def _coerce_value(column_type: Any, value: Any) -> Any:
    if value is None:
        return None
    if isinstance(column_type, Boolean):
        if isinstance(value, str):
            normalized = value.casefold().strip()
            if normalized in {"1", "true", "t", "yes", "y", "-1"}:
                return True
            if normalized in {"0", "false", "f", "no", "n", ""}:
                return False
        return bool(value)
    if isinstance(column_type, Integer):
        return int(value)
    if isinstance(column_type, (Float, Numeric)):
        return Decimal(str(value))
    if isinstance(column_type, (Date, DateTime, Time)):
        if isinstance(value, (date, datetime, time)):
            return value
        return _parse_temporal_value(str(value), column_type.python_type)
    return value


def prepare_access_row(model: type[DeclarativeBase], source_row: Mapping[str, Any]) -> dict[str, Any]:
    lookup = _source_lookup(source_row)
    mapper = inspect(model)
    prepared: dict[str, Any] = {}

    for attribute in mapper.column_attrs:
        column = attribute.columns[0]
        attr_name = attribute.key
        if should_skip_access_column(attr_name) or should_skip_access_column(column.name):
            continue

        for candidate in (
            normalize_access_identifier(attr_name),
            normalize_access_identifier(column.name),
        ):
            if candidate not in lookup:
                continue
            prepared[attr_name] = _coerce_value(column.type, lookup[candidate])
            break

    return prepared
