# ADR 008: Customer Market Assignment Model

**Date:** 2026-04-19  
**Status:** Accepted  
**Authors:** The AI, project team  
**Drivers:** F-009 (Customer Market Assignment), F-003 (Customer CRUD)  
**Tags:** model, relationship, customer, market, alembic, SQLAlchemy

## Decision
Implement a many-to-many relationship between Customer and Market using a join table (customer_market). Add Market and CustomerMarket models, and update Customer and Market models to support bidirectional relationships.

## Context
- F-009 requires mapping customers to one or more markets (and future MarketSub).
- No prior Market or customer-market association existed.
- SQLAlchemy and Alembic are used for ORM and migrations.
- F-003 (Customer CRUD) is a dependency.

## Alternatives Considered
- **Single market per customer:** Too restrictive for business needs.
- **Denormalized market field on Customer:** Not scalable, no referential integrity.
- **Many-to-many with join table:** Standard, scalable, supports future MarketSub.

## Implementation Details
- Added Market model (market table) with unique name.
- Added CustomerMarket join model (customer_market table).
- Updated Customer and Market models with relationship fields.
- Alembic migration created and applied.
- Unit test verifies assignment and retrieval.

## Validation
- Unit test: Customer can be assigned to Market and retrieved via relationship.
- All tests pass after migration.
- Alembic migration applied successfully.

## Consequences
- Enables flexible market assignment for customers.
- Foundation for future MarketSub and lookup table expansion.
- Minimal performance impact; standard SQLAlchemy pattern.

## Monitoring & Rollback
- Review after MarketSub implementation.
- Rollback: Drop customer_market and market tables if needed.

## References
- F-009 in prd.json
- SQLAlchemy documentation: Many-to-many relationships
- Alembic migration scripts
