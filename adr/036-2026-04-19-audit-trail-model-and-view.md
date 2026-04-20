# ADR 036: Audit Trail Model and View

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI
- Drivers: F-036 backlog item, field-level history requirements, consistency with Flask/SQLAlchemy patterns
- Tags: audit trail, history, Flask, SQLAlchemy, customer

## Decision
Implement a dedicated `tblaudittrail` table, a small audit-trail service for recording field changes, and a read-only audit-history route for viewing per-record history.

## Context
The backlog requires old/new value tracking for create, edit, and delete events and a way to inspect history by record. The codebase already uses server-rendered Flask routes and explicit model/service boundaries, so a dedicated table plus explicit form hooks fits the existing architecture.

## Alternatives Considered
- SQLAlchemy mapper/session event listeners: rejected because they hide business intent and make per-form behavior harder to reason about.
- Database triggers: rejected because they move application logic out of Python and complicate tests and portability.
- Per-model ad hoc logging: rejected because it duplicates logic and would be difficult to reuse across future forms.

## Implementation Details
- Added `AuditTrail` mapped to `tblaudittrail` with table name, record id, field name, old value, new value, action, and timestamp.
- Added `record_audit_change()` and `get_audit_history()` helpers in `src/ith_webapp/services/audit_trail.py`.
- Updated customer create/edit/delete routes to write audit rows alongside normal form saves.
- Added `/audit-trail/<table_name>/<record_id>` to render history for a record.
- Added a migration for `tblaudittrail` and a simple history template.

## Validation
- `pytest -q tests/unit/test_audit_trail.py` passes.
- `pytest -q` passes for the full repository.

## Consequences
- Audit history is explicit, testable, and reusable.
- Customer forms now write extra rows during writes, which adds a small persistence cost.
- The implementation stays portable across SQLite and the target database.

## Monitoring & Rollback
- Review after the next non-customer form needs audit history.
- Rollback by removing the audit model, service, blueprint, template, migration, and customer hooks if the approach is superseded.

## References
- F-036 in `prd.json`
- `src/ith_webapp/models/audit_trail.py`
- `src/ith_webapp/services/audit_trail.py`
- `src/ith_webapp/views/audit_trail.py`
- `src/ith_webapp/views/customers.py`
- `migrations/versions/2026_04_19_10_add_audit_trail_table.py`
- `tests/unit/test_audit_trail.py`
