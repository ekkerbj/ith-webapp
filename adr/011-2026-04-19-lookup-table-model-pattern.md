# ADR 011: Lookup Table Model Pattern

- Date: 2026-04-19
- Status: Accepted
- Authors: The AI
- Drivers: F-010 requirement for reference/lookup tables
- Tags: models, SQLAlchemy, lookup, reference, pattern

## Decision

Adopt a uniform SQLAlchemy model pattern for all lookup/reference tables (e.g., classification, failure_class, etc.), each with an integer primary key and unique name field.

## Context

F-010 requires models for all reference/lookup tables, supporting CRUD and mapping to Access/SAP data. Consistency and maintainability are critical.

## Alternatives Considered

- Ad-hoc models for each table (rejected: increases duplication)
- Single generic lookup table (rejected: loses type safety, referential clarity)

## Implementation Details

Each lookup table (e.g., Classification) is implemented as a SQLAlchemy model with:
- Integer primary key (autoincrement)
- Unique, non-null name field
- Registered in models/__init__.py for metadata reflection

## Validation

- Unit test for Classification model: create, persist, retrieve, assert name
- Table auto-created by Base.metadata.create_all
- Test passes in CI

## Consequences

+ Consistent, DRY model structure
+ Easy to add new lookup tables
+ Supports admin CRUD
- Slightly more boilerplate per table

## Monitoring & Rollback

- Review: 2026-05-01
- Success: All lookup tables implemented and tested
- Rollback: Revert to ad-hoc models if pattern proves too rigid

## References

- F-010 in prd.json
- SQLAlchemy documentation
- Existing model files
