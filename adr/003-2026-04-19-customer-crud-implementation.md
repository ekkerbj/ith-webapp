# ADR 003: Customer CRUD Implementation

## Metadata
- **Date:** 2026-04-19
- **Status:** Accepted
- **Authors:** The AI, project team
- **Drivers:** CRUD for core business entity, TDD, maintainability, Access migration
- **Tags:** customer, CRUD, model, repository, view, TDD

## Decision
Implement Customer CRUD (Create, Read, Update, Delete) as the first business entity. Map 11 core columns from Access to SQLAlchemy model. Provide repository with find_by_id, find_all, save. Expose full CRUD views (list, detail, create, edit) with server-rendered HTML. All logic covered by unit and integration tests.

## Context
- Customer is the root entity for most business workflows.
- Access app has ~80 columns; only 11 core fields are required for MVP.
- TDD is mandatory; all code must be test-driven.
- Layered architecture: model, repository, service, view, template.

## Alternatives Considered
- Implementing all 80+ columns: rejected for MVP, complexity too high.
- Skipping repository layer: rejected, would couple views to ORM.
- Using generic CRUD generator: rejected, explicit code preferred for clarity and testability.

## Implementation Details
- SQLAlchemy model: 11 fields, mapped 1:1 to Access columns.
- Repository: find_by_id, find_all, save methods.
- Views: Flask routes for list, detail, create, edit.
- Templates: Jinja2 for all views.
- Tests: pytest unit tests for model, repository, views; integration tests for end-to-end CRUD.

## Validation
- All unit and integration tests pass (pytest, SQLite in-memory).
- Manual browser check: create, edit, list, and detail all work as expected.
- Code reviewed for TDD and Clean Code compliance.

## Consequences
**Positive:**
- Foundation for all customer-related features.
- Demonstrates TDD and layered architecture.
- Enables rapid onboarding for new developers.

**Negative:**
- Only 11 columns implemented; future work needed for full migration.
- Some duplication in test setup (mitigated by fixtures).

**Neutral:**
- Explicit repository layer adds a small amount of boilerplate.

## Monitoring & Rollback
- Review after first dependent feature (e.g., Customer Address) is implemented.
- Rollback by reverting to previous commit if major issues found.

## References
- prd.json F-003
- tests/unit/test_customer_model.py
- tests/unit/test_customer_repository.py
- tests/unit/test_customer_views.py
