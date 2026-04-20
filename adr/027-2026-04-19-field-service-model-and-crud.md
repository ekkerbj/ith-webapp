# ADR 027: Field Service Model and CRUD

- Date: 2026-04-19
- Status: Accepted
- Authors: The AI
- Drivers: F-029 field service backlog item, consistency with existing SQLAlchemy CRUD patterns, lookup-table reuse
- Tags: model, migration, views, field-service, lookup
- Supersedes: None
- Superseded By: None

## Decision

Implement `FieldService` as a customer-linked visit record with `FieldServiceStatus`, `FieldServiceType`, and `FieldServiceSub` lookup models, plus CRUD views for field service records.

## Context

F-029 requires a field service header record tied to `Customer`, along with status and type/sub lookup tables. The codebase already uses simple SQLAlchemy models, per-feature migrations, and lightweight Flask blueprints for CRUD screens.

## Alternatives Considered

- Add only the field service header table: rejected because the backlog explicitly calls for status and type/sub lookup tables.
- Model lookups as a single generic reference table: rejected because the project uses explicit models for each reference domain.

## Implementation Details

- `FieldService` stores `customer_id`, `field_service_status_id`, `visit_date`, and `visit_notes`.
- `FieldServiceStatus` and `FieldServiceType` follow the existing lookup-table pattern with unique names.
- `FieldServiceSub` references `FieldServiceType` to preserve the type/sub structure.
- `field_services` blueprint provides list, detail, create, edit, and delete routes.
- Templates were added for list, detail, and form rendering.
- Alembic migration `2026_04_19_04` creates all four tables.

## Validation

- Unit tests cover `FieldService`, `FieldServiceStatus`, `FieldServiceType`, `FieldServiceSub`, and CRUD views.
- In-memory database tests verify persistence, retrieval, redirects, and HTML rendering.

## Consequences

- Field service records can now be created and managed through the web app.
- Lookup data is normalized and reusable.
- Adds a small amount of schema and view boilerplate.

## Monitoring & Rollback

- Review: 2026-05-01
- Success: field service records and lookup rows can be created, edited, listed, and deleted without regressions.
- Rollback: revert the migration, model, view, template, and test additions if needed.

## References

- prd.json F-029
- adr/011-2026-04-19-lookup-table-model-pattern.md
- src/ith_webapp/models/field_service.py
- src/ith_webapp/views/field_service.py
- migrations/versions/2026_04_19_04_add_field_service_tables.py
