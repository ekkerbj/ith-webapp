# ADR 020: Service Sub Copy (Quote Snapshots)

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI
- Drivers: F-021 (Service Sub Copy), quote snapshotting, historical pricing
- Tags: service_sub_copy, snapshot, model, database, SQLAlchemy, architecture
- Supersedes: None
- Superseded By: None

## Decision
Introduce a ServiceSubCopy model and service_sub_copy table to support F-021, representing a snapshot of service line items at the time a quote is sent. This preserves historical pricing and itemization, even if current prices change.

## Context
F-021 requires the ability to capture a point-in-time copy of all service line items (parts/labor) for a given service order, to preserve the state of a quote as sent to the customer. This is necessary for auditability, customer communication, and accurate historical reporting.

## Alternatives Considered
- Storing only references to current ServiceSub: Rejected, as changes to ServiceSub would retroactively alter historical quotes.
- Using a JSON blob: Rejected for lack of schema enforcement and queryability.
- Versioning ServiceSub: Rejected for complexity and risk of accidental mutation.

## Implementation Details
- Create ServiceSubCopy model in src/ith_webapp/models/service_sub_copy.py.
- Define service_sub_copy table with fields: id (PK), service_id (FK), item_type, quantity, price, cost, snapshot_date.
- Populate ServiceSubCopy entries when a quote is sent (triggered by business logic).
- Alembic migration for table creation.
- Import in models/__init__.py.

## Validation
- Unit test for ServiceSubCopy creation and relationship to Service.
- Alembic migration applies and reverts cleanly.
- Table appears in test and production DBs.
- Confirmed that historical data is preserved after ServiceSub changes.

## Consequences
+ Enables quote snapshotting and historical pricing
+ Preserves audit trail for customer quotes
- Increases schema and code complexity

## Monitoring & Rollback
- Review after initial implementation and test coverage.
- Rollback by reverting migration and model file if issues arise.

## References
- F-021 in prd.json
- ADR 014: ServiceSub Model and Table
- Alembic migration for service_sub_copy table
