from collections.abc import Mapping
from typing import Any

from sqlalchemy.orm import Session

from ith_webapp.models.audit_trail import AuditTrail


def _stringify(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def record_audit_change(
    session: Session,
    *,
    table_name: str,
    record_id: int,
    action: str,
    changes: Mapping[str, tuple[Any, Any]],
) -> list[AuditTrail]:
    entries: list[AuditTrail] = []
    for field_name, (old_value, new_value) in changes.items():
        entry = AuditTrail(
            table_name=table_name,
            record_id=record_id,
            field_name=field_name,
            old_value=_stringify(old_value),
            new_value=_stringify(new_value),
            action=action,
        )
        session.add(entry)
        entries.append(entry)
    return entries


def get_audit_history(session: Session, *, table_name: str, record_id: int) -> list[AuditTrail]:
    return (
        session.query(AuditTrail)
        .filter_by(table_name=table_name, record_id=record_id)
        .order_by(AuditTrail.changed_at.asc(), AuditTrail.audit_trail_id.asc())
        .all()
    )
