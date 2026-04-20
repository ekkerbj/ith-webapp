# ADR 075: Audit Trail Report and User Tracking

## Metadata
- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-075 backlog item, Access change-log parity, per-user filtering, explicit audit history
- **Tags**: audit-trail, reporting, Flask, SQLAlchemy, access-parity

## Decision
Extend audit trail persistence with a nullable `changed_by` column, record the current signed-in user email on customer audit writes, and expose an HTML audit-trail report at `/reports/audit-trail` with entity, field, user, and date-range filters.

## Context
The existing audit-trail feature already stores field-level before/after values and supports per-record history. The backlog now requires a broader change-log report comparable to the Access Change Log reports, including filtering by entity, field, user, and date range.

## Alternatives Considered
- **Keep audit data without user attribution**: Rejected because user filtering would not be meaningful.
- **Derive user from request logs**: Rejected because the report should query application data, not logs.
- **Build the report from ad hoc joins without a persisted user column**: Rejected because the audit trail needs durable actor attribution.

## Implementation Details
- Added `changed_by` to `tblaudittrail` and the `AuditTrail` model.
- Updated `record_audit_change()` to accept an optional `changed_by` value.
- Customer create/edit/delete routes now capture the signed-in user email from the Flask session.
- Added `/reports/audit-trail` to render a filterable HTML report over audit rows.
- Added a migration to add `changed_by` to the table and updated the existing history view to display the actor when present.

## Validation
- Added regression coverage for the report filters and user attribution.
- Ran `pytest -q`; the full suite passes with 165 tests.

## Consequences
- Audit history can now be filtered by actor, which matches the legacy change-log workflow more closely.
- Customer writes gain one additional nullable column write with no behavioral impact when no user is available.
- Existing audit history remains valid because the new column is nullable.

## Monitoring & Rollback
- **Review date**: 2026-05-04
- **Success metric**: audit trail report filters correctly by entity, field, user, and date range while customer writes continue to persist history rows.
- **Rollback strategy**: remove the report route, user-attribution column, customer session hook, and migration if the legacy report shape changes.

## References
- `prd.json` F-075
- `src/ith_webapp/models/audit_trail.py`
- `src/ith_webapp/services/audit_trail.py`
- `src/ith_webapp/views/customers.py`
- `src/ith_webapp/reports.py`
- `src/ith_webapp/templates/audit_trail/history.html`
- `migrations/versions/2026_04_20_02_add_audit_trail_changed_by.py`
- `tests/unit/test_audit_trail.py`
