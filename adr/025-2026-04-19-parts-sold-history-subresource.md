# ADR 025: Parts Sold History Model and Subresource View

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI, project team
- Drivers: F-027 requirement for parts sold history and part detail subresource
- Tags: parts, history, model, migration, Flask, routing

## Decision
Implement a `PartsSold` SQLAlchemy model, Alembic migration for the `parts_sold` table, and a Flask subresource view under `/parts/<part_id>/sold-history`. Register the `Part` and `PartsSold` models in the model package so schema creation includes both tables.

## Context
F-027 requires tracking parts sales history per part and exposing that history as a subresource of the Part detail page. The codebase already had a `Part` model, but it was not registered in the model package, and no sold-history model or view existed.

## Alternatives Considered
- Model only, no view: Rejected because the backlog item explicitly calls for a subresource view.
- Reuse an unrelated workflow or customer route: Rejected because parts history has its own resource boundary and URL space.
- Delay migration until later: Rejected because the schema should stay aligned with the ORM model.

## Implementation Details
- Added `PartsSold` with `id`, `part_id`, `quantity`, and `sold_date`.
- Added an Alembic migration creating `parts_sold` with a foreign key to `part.part_id`.
- Registered `Part`, `PartsList`, `PartsSub`, and `PartsSold` in `src/ith_webapp/models/__init__.py`.
- Added a `parts` blueprint with `/parts/<part_id>` and `/parts/<part_id>/sold-history` routes.
- Added templates for part detail and sold history.

## Validation
- `pytest -q` passes.
- New unit coverage verifies the sold-history subresource renders the seeded part and sale record.

## Consequences
- Parts sales can now be recorded and displayed per part.
- App startup now includes the part-related tables in `Base.metadata.create_all`.
- Adds a new blueprint and templates for the parts area.

## Monitoring & Rollback
- Review after the next parts-related backlog item lands.
- Rollback: remove the blueprint, model registration, migration, and templates if F-027 is superseded.

## References
- F-027 in `prd.json`
- `src/ith_webapp/models/parts_sold.py`
- `src/ith_webapp/views/parts.py`
- `tests/unit/test_parts_views.py`
