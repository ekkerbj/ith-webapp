# ADR 015: Service Time Tracking Model and Migration

**Date:** 2026-04-19  
**Status:** Accepted  
**Authors:** The AI, project team  
**Drivers:** F-016 in prd.json  
**Tags:** model, migration, service, time-tracking  
**Supersedes/Superseded By:** None

## Decision
Implement a `ServiceTime` model and corresponding Alembic migration to support labor time tracking as a sub-resource of Service. The model includes technician, hours, date, and labor rate fields, and is mapped to the `service_time` table.

## Context
The project requires tracking labor time entries per service order, including technician, hours, date, and labor rate, as described in F-016. This supports accurate billing and reporting for service work.

## Alternatives Considered
- **Store time tracking as JSON in Service:** Rejected for lack of queryability and normalization.
- **Embed in ServiceSub:** Rejected due to different semantics and reporting needs.
- **Separate table (chosen):** Enables normalized, queryable, and extensible time tracking.

## Implementation Details
- Created `ServiceTime` SQLAlchemy model in `models/service_time.py`.
- Added import to `models/__init__.py`.
- Generated Alembic migration for `service_time` table.
- Test added/updated in `test_service_model.py`.

## Validation
- Unit test verifies creation and persistence of `ServiceTime` records.
- Alembic migration applied and schema verified.
- All tests pass after implementation.

## Consequences
- Enables extensible, normalized time tracking for service orders.
- Minimal impact on existing code; new table and model only.
- Supports future reporting and analytics on labor time.

## Monitoring & Rollback
- Review after first production use for data integrity and reporting needs.
- Rollback by dropping `service_time` table and reverting migration if needed.

## References
- F-016 in prd.json
- test_service_model.py
- Alembic migration f495e42e6930
