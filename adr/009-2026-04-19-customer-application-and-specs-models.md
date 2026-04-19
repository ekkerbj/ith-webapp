# ADR 009: Customer Application and Specs Models

**Date:** 2026-04-19  
**Status:** Accepted  
**Authors:** The AI, project team  
**Drivers:** F-008 (Customer Application and Specs), F-003 (Customer CRUD)  
**Tags:** model, relationship, customer, application, specs, alembic, SQLAlchemy

## Decision
Implement CustomerApplication and CustomerApplicationSpecs models and tables. Each customer can have multiple applications, and each application can have multiple specs. CRUD operations will be provided as sub-resources of Customer.

## Context
- F-008 requires tracking what customers use tools for, including application details and specifications.
- No prior customer_application or customer_application_specs tables exist.
- SQLAlchemy and Alembic are used for ORM and migrations.
- F-003 (Customer CRUD) is a dependency.

## Alternatives Considered
- **Single application/spec per customer:** Too restrictive for business needs.
- **Denormalized fields on Customer:** Not scalable, no referential integrity.
- **Separate tables with relationships:** Standard, scalable, supports future expansion.

## Implementation Details
- Add CustomerApplication model (customer_application table) with FK to customer.
- Add CustomerApplicationSpecs model (customer_application_specs table) with FK to customer_application.
- Update Customer model with relationship to applications.
- Alembic migration to create both tables.
- Unit and integration tests for persistence and retrieval.

## Validation
- Unit tests: Customer can have applications and specs persisted and retrieved.
- Alembic migration applies cleanly.
- All tests pass after implementation.

## Consequences
- Enables flexible tracking of customer applications and specs.
- Foundation for future reporting and analytics.
- Minimal performance impact; standard SQLAlchemy pattern.

## Monitoring & Rollback
- Review after first production use.
- Rollback: Drop customer_application and customer_application_specs tables if needed.

## References
- F-008 in prd.json
- SQLAlchemy documentation: One-to-many and many-to-one relationships
- Alembic migration scripts
