# ADR 032: Projects Model and CRUD

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI, project team
- Drivers: F-032 projects backlog item, consistency with existing lightweight SQLAlchemy/Flask CRUD patterns
- Tags: projects, model, migration, Flask, CRUD, customer

## Decision
Implement a dedicated `Project` SQLAlchemy model, an Alembic migration for the `projects` table, and a Flask CRUD blueprint under `/projects`.

## Context
F-032 requires project tracking linked to customers via cardcode. The codebase already uses simple resource-specific ORM models, one blueprint per resource, and server-rendered Jinja2 views, so the Projects feature should follow the same pattern instead of introducing a generic form or service layer abstraction.

## Alternatives Considered
- Store projects on `Customer`: rejected because projects are a first-class record with their own lifecycle.
- Model projects without a dedicated table: rejected because the backlog explicitly requires a `projects` table.
- Add only a read-only view: rejected because the backlog calls for CRUD views.

## Implementation Details
- Added `Project` with `project_id`, `customer_id`, `cardcode`, `project_name`, and `active`.
- Registered `Project` in `src/ith_webapp/models/__init__.py` so metadata creation includes the table.
- Added a `projects` blueprint with list, detail, create, edit, and delete routes.
- Added templates for list, detail, and form rendering.
- Added an Alembic migration to create the `projects` table.

## Validation
- `pytest -q` passes for the full repository.
- Unit coverage verifies model fields and CRUD route behavior for list, detail, create, edit, and delete.
- The new model and migration files compile successfully.

## Consequences
- Projects can now be stored and managed as a dedicated customer-linked resource.
- The app gains one more blueprint and one more table in the schema.
- Future work may refine the customer linkage if the Access source reveals more project-specific fields.

## Monitoring & Rollback
- Review after the next customer-linked operational workflow lands.
- Rollback: remove the blueprint, templates, migration, model registration, and tests if the resource is superseded.

## References
- F-032 in `prd.json`
- `src/ith_webapp/models/project.py`
- `src/ith_webapp/views/projects.py`
- `migrations/versions/2026_04_19_06_add_projects_table.py`
- `tests/unit/test_project_model.py`
- `tests/unit/test_project_views.py`
