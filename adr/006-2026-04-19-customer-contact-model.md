# ADR 006: Customer Contact Model and Migration

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI
- Drivers: PRD F-006, relational integrity, extensibility
- Tags: model, migration, SQLAlchemy, Alembic

## Decision
Implement a `CustomerContact` model and corresponding `customer_contact` table, supporting multiple contacts per customer, with Alembic migration and test coverage.

## Context
- PRD F-006 requires customer contact management as a sub-resource of Customer.
- Each customer may have multiple contacts (name, email, phone, position).
- SQLAlchemy is the ORM; Alembic is used for migrations.

## Alternatives Considered
- **Single contact field on Customer**: Not flexible for multiple contacts; rejected.
- **No migration**: Would not persist data; rejected.
- **No test coverage**: Violates TDD and project standards; rejected.

## Implementation Details
- Added `CustomerContact` model in `src/ith_webapp/models/customer_contact.py`.
- Added Alembic migration for `customer_contact` table.
- Updated `__init__.py` to expose the model.
- Created unit test for persistence and retrieval.

## Validation
- All tests pass (unit test for model CRUD).
- Alembic migration applies cleanly.

## Consequences
- Enables extensible contact management per customer.
- Maintains referential integrity via foreign key.
- Increases schema complexity slightly.

## Monitoring & Rollback
- Review: 2026-05-01
- Success: Continued test pass, no migration issues, feature use in production.
- Rollback: Drop table and revert migration if issues arise.

## References
- PRD F-006
- SQLAlchemy, Alembic documentation
- Previous ADRs on model/migration patterns
