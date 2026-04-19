# ADR 010: Customer Tools Model and Sub-Model

**Date:** 2026-04-19  
**Status:** Accepted  
**Authors:** The AI, project team  
**Drivers:** F-011 (Customer Tools), F-003 (Customer CRUD), F-010 (Lookup Tables)  
**Tags:** model, relationship, customer, tools, alembic, SQLAlchemy

## Decision
Implement CustomerTools and CustomerToolsSub models and tables. Each customer can have multiple tools, each tool can have multiple sub-records. Tools are linked to the unit table. CRUD operations are provided as sub-resources of Customer.

## Context
- F-011 requires tracking tools owned by each customer, including serial numbers, fab numbers, model info, and sub-records.
- No prior customer_tools or customer_tools_sub tables existed.
- SQLAlchemy and Alembic are used for ORM and migrations.
- F-003 (Customer CRUD) and F-010 (Lookup Tables) are dependencies.

## Alternatives Considered
- **Single tool per customer:** Too restrictive for business needs.
- **Denormalized fields on Customer:** Not scalable, no referential integrity.
- **Separate tables with relationships:** Standard, scalable, supports future expansion.

## Implementation Details
- Add CustomerTools model (customer_tools table) with FK to customer and unit.
- Add CustomerToolsSub model (customer_tools_sub table) with FK to customer_tools.
- Update Customer model with relationship to tools.
- Alembic migrations to create all tables.
- Unit and integration tests for persistence and retrieval.

## Validation
- Unit tests: Customer can have tools and sub-records persisted and retrieved.
- Alembic migration applies cleanly.
- All tests pass after implementation.

## Consequences
- Enables flexible tracking of customer tools and sub-records.
- Foundation for future reporting and analytics.
- Minimal performance impact; standard SQLAlchemy pattern.

## Monitoring & Rollback
- Review after first production use.
- Rollback: Drop customer_tools and customer_tools_sub tables if needed.

## References
- F-011 in prd.json
- SQLAlchemy documentation: One-to-many and many-to-one relationships
- Alembic migration scripts
