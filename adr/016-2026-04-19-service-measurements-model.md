# ADR 016: Service Measurements Model and Table

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors/Owners: Team
- Drivers: F-017 requirement, inspection checklist per service order
- Tags: model, migration, SQLAlchemy, checklist
- Supersedes/Superseded By: None

## Decision
Implement a `ServiceMeasurements` SQLAlchemy model and corresponding `service_measurements` table to track inspection checklist data per service order, supporting multiple tool types and ~100 boolean/numeric fields.

## Context
The Access database uses six specialized forms for tool-type-specific inspection checklists. The new system must support extensible, normalized storage for these fields, linked to each service order.

## Alternatives Considered
- Single denormalized table with all fields (chosen for simplicity and migration ease)
- Multiple tables per tool type (rejected: complexity, maintenance overhead)
- EAV (entity-attribute-value) schema (rejected: query complexity, performance)

## Implementation Details
- SQLAlchemy model: `ServiceMeasurements` in `models/service_measurements.py`
- Table: `service_measurements` with representative fields for each tool type
- Alembic migration generated and applied
- Relationship to `Service` model via `service_id` FK

## Validation
- Unit test for model field assignment and defaults
- Alembic migration applied successfully
- Test suite passes

## Consequences
- Positive: Simple queries, easy migration, clear linkage to service orders
- Negative: Table may grow wide as more fields are added
- Neutral: Future refactoring possible if requirements change

## Monitoring & Rollback
- Review: 2026-06-01
- Success metrics: All checklist data captured, no migration issues
- Rollback: Drop table and revert migration if needed

## References
- F-017 in prd.json
- Access inspection forms
- SQLAlchemy documentation
