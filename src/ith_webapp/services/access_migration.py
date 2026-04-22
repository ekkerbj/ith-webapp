from __future__ import annotations

from collections.abc import Mapping
import csv
from datetime import date, datetime, time
from decimal import Decimal
from io import StringIO
import subprocess
import re
from pathlib import Path
from typing import Any

from ith_webapp.database import Base
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


def migration_models(metadata: MetaData) -> list[type[DeclarativeBase]]:
    models: list[type[DeclarativeBase]] = []
    mapped_models = {mapper.local_table.name: mapper.class_ for mapper in Base.registry.mappers}
    for table in migration_tables(metadata):
        model = mapped_models.get(table.name)
        if model is not None:
            models.append(model)
    return models


def assert_empty_database(session, metadata: MetaData) -> None:
    for table in metadata.sorted_tables:
        if session.query(table).first() is not None:
            raise RuntimeError("target database must be empty before import")


def _run_mdb_command(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, capture_output=True)
    return completed.stdout.decode("utf-8", errors="replace")


def list_access_tables(access_file: str | Path) -> list[str]:
    output = _run_mdb_command(["mdb-tables", "-1", str(access_file)])
    return [line.strip() for line in output.splitlines() if line.strip()]


def export_access_rows(access_file: str | Path, table_name: str) -> list[dict[str, Any]]:
    output = _run_mdb_command(["mdb-export", str(access_file), table_name])
    reader = csv.DictReader(StringIO(output))
    return [dict(row) for row in reader]


def import_access_data(session, access_file: str | Path, metadata: MetaData) -> None:
    assert_empty_database(session, metadata)
    tables = {normalize_access_identifier(name): name for name in list_access_tables(access_file)}

    for model in migration_models(metadata):
        table_name = getattr(model, "__tablename__", None)
        if table_name is None:
            continue
        access_table_name = tables.get(normalize_access_identifier(table_name))
        if access_table_name is None:
            continue
        for source_row in export_access_rows(access_file, access_table_name):
            prepared = prepare_access_row(
                model,
                source_row,
                access_table_name=access_table_name,
            )
            if any(
                not column.nullable
                and not column.primary_key
                and prepared.get(attribute.key) is None
                for attribute in inspect(model).column_attrs
                for column in attribute.columns
            ):
                continue
            session.add(model(**prepared))

    session.commit()


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
    if isinstance(value, str) and not value.strip():
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


def prepare_access_row(
    model: type[DeclarativeBase],
    source_row: Mapping[str, Any],
    access_table_name: str | None = None,
) -> dict[str, Any]:
    lookup = _source_lookup(source_row)
    mapper = inspect(model)
    prepared: dict[str, Any] = {}

    if getattr(model, "__tablename__", None) == "tblaudittrail":
        special_mapping = {
            "table_name": lookup.get("formname"),
            "record_id": lookup.get("recordid"),
            "field_name": lookup.get("fieldname") or "(record)",
            "old_value": lookup.get("oldvalue"),
            "new_value": lookup.get("newvalue"),
            "action": lookup.get("action"),
            "changed_by": lookup.get("username"),
        }
        for key, value in special_mapping.items():
            if value is not None:
                prepared[key] = _coerce_value(mapper.attrs[key].columns[0].type, value)

    for attribute in mapper.column_attrs:
        column = attribute.columns[0]
        attr_name = attribute.key
        if should_skip_access_column(attr_name) or should_skip_access_column(column.name):
            continue

        for candidate in (
            normalize_access_identifier(attr_name),
            normalize_access_identifier(column.name),
            normalize_access_identifier(access_table_name or "") if attr_name == "name" else "",
        ):
            if candidate not in lookup:
                continue
            candidate_value = lookup[candidate]
            if attr_name == "name" and isinstance(candidate_value, str) and not candidate_value.strip():
                break
            prepared[attr_name] = _coerce_value(column.type, candidate_value)
            break

    return prepared
