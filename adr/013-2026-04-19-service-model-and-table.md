# ADR 013: Service Model and Table Introduction

## Metadata
- Date: 2026-04-19
- Status: Proposed
- Authors: The AI
- Drivers: F-014 Service Header feature, relational integrity, extensibility
- Tags: service, model, database, SQLAlchemy, architecture

## Decision
Introduce a new Service model and service table to support the F-014 Service Header feature, with relationships to Customer and CheckInSub, and fields as specified in prd.json.

## Context
The F-014 feature requires a Service entity representing a quote/work order, linked to Customer and CheckInSub, with ~100+ fields. This entity is central to the workflow and must support CRUD operations and integration with related models.

## Alternatives Considered
- Embedding service data in CheckInSub: Rejected due to lack of separation of concerns and scalability.
- Using a generic key-value store: Rejected for lack of schema enforcement and queryability.
- Implementing as a flat file: Rejected for lack of relational integrity and performance.

## Implementation Details
- Create a Service model in src/ith_webapp/models/service.py.
- Define a service table with fields: service_id (PK), customer_id (FK), check_in_sub_id (FK), cardcode, order_status, sale_type, dates, technician, pricing fields, etc.
- Establish relationships to Customer and CheckInSub.
- Integrate with Alembic for migrations.
- Add to __init__.py and __all__.

## Validation
- Unit and integration tests for CRUD operations.
- Alembic migration applies cleanly and is reversible.
- Relationships enforce referential integrity.

## Consequences
+ Enables F-014 and downstream features (F-015, etc.)
+ Centralizes service logic and data
- Increases schema complexity

## Monitoring & Rollback
- Review after initial implementation and test coverage.
- Rollback by reverting migration and model file if issues arise.

## References
- prd.json F-014
- SQLAlchemy documentation
- Existing model patterns in ith-webapp
