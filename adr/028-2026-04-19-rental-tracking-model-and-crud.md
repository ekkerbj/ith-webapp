# ADR 028: Rental Tracking Model and CRUD Views

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI, project team
- Drivers: F-031 rental tracking backlog item, reuse of existing SQLAlchemy/Flask CRUD patterns, lookup-table support
- Tags: rental, model, migration, Flask, CRUD, lookup

## Decision
Implement a dedicated `Rental` SQLAlchemy model, a `RentalStatus` lookup model, an Alembic migration for both tables, and a Flask CRUD blueprint under `/rentals`.

## Context
F-031 requires rental tracking for tools and a status lookup. The codebase already models customers, customer tools, and lookup tables as explicit SQLAlchemy classes with lightweight Flask CRUD views, so the rental feature should follow the same shape instead of introducing a generic or nested implementation.

## Alternatives Considered
- Store rental state on `CustomerTools`: rejected because rentals are lifecycle records, not intrinsic tool attributes.
- Reuse `FieldServiceStatus` for rental lifecycle state: rejected because rental state is a distinct domain and deserves its own lookup table.
- Model rentals without a status table: rejected because the backlog explicitly calls for `rental_status` lookup support.

## Implementation Details
- Added `Rental` with `customer_id`, `customer_tools_id`, `rental_status_id`, `rental_date`, and `return_date`.
- Added `RentalStatus` with a unique `name` field.
- Registered both models in `src/ith_webapp/models/__init__.py` so metadata creation includes the tables.
- Added a `rentals` blueprint with list, detail, create, edit, and delete routes.
- Added templates for list, detail, and form rendering.
- Added an Alembic migration to create `rental_status` and `rental`.

## Validation
- `pytest -q tests/unit/test_rental_tracking.py` passes.
- `pytest -q` passes for the full repository.
- Unit coverage verifies persistence, list/detail rendering, and CRUD redirects.

## Consequences
- Rental records can now be stored and managed through the web app.
- Tool rental status is normalized and reusable.
- The schema and navigation gain one more resource, increasing maintenance surface slightly.

## Monitoring & Rollback
- Review after the next inventory or tool-tracking feature lands.
- Rollback: remove the blueprint, templates, migration, model registration, and tests if the rental resource is superseded.

## References
- F-031 in `prd.json`
- `src/ith_webapp/models/rental.py`
- `src/ith_webapp/models/rental_status.py`
- `src/ith_webapp/views/rentals.py`
- `tests/unit/test_rental_tracking.py`
