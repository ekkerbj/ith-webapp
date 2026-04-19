# ADR 014: ServiceSub Model and Table

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI
- Drivers: F-015 Service Sub Items, line item extensibility, relational integrity
- Tags: service_sub, model, database, SQLAlchemy, architecture
- Supersedes: None
- Superseded By: None

## Decision
Introduce a ServiceSub model and service_sub table to support F-015, representing line items (parts/labor) on a service order. Includes item type, quantity, price, cost, and supports nesting (sub-sub items).

## Context
F-015 requires detailed tracking of service order line items, both parts and labor, with support for nested sub-items. The model must support CRUD as a sub-resource of Service, and maintain referential integrity with Service.

## Alternatives Considered
- Embedding line items in Service: Rejected for lack of normalization and flexibility.
- Using a generic JSON field: Rejected for lack of schema enforcement and queryability.
- Flat file or external system: Rejected for lack of integration and transactional safety.

## Implementation Details
- Create ServiceSub model in src/ith_webapp/models/service_sub.py.
- Define service_sub table with fields: service_sub_id (PK), service_id (FK), item_type, quantity, price, cost, parent_sub_id (for nesting).
- Establish relationship to Service and self (for nesting).
- Alembic migration for table creation.
- Import in models/__init__.py.

## Validation
- Unit test for ServiceSub creation and relationship to Service.
- Alembic migration applies and reverts cleanly.
- Table appears in test and production DBs.

## Consequences
+ Enables F-015 and downstream features (quote snapshots, reports)
+ Normalizes line item data
- Increases schema complexity

## Monitoring & Rollback
- Review after initial implementation and test coverage.
- Rollback by reverting migration and model file if issues arise.

## References
- F-015 in prd.json
- ADR 013: Service Model and Table
- Alembic migration 55133538af72_add_service_sub_table.py
