# ADR 034: ITH Test Gauge Tracking Model and CRUD

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI, project team
- Drivers: F-034 backlog item, consistency with the existing lightweight SQLAlchemy + Flask CRUD pattern, schema support for calibration and certification tracking
- Tags: gauge, model, migration, CRUD, Flask, SQLAlchemy

## Decision
Implement ITH Test Gauge tracking as two dedicated tables: `ith_test_gauge_type` for lookup values and `ith_test_gauge` for individual gauge records, exposed through a Flask CRUD blueprint under `/ith-test-gauges`.

## Context
F-034 requires internal calibration gauge tracking and certification. The application already uses small resource-specific models, direct Flask blueprints, and server-rendered Jinja templates, so the new feature should follow the same approach instead of introducing a generic admin framework or a shared polymorphic asset model.

## Alternatives Considered
- Store gauge data on an existing resource: rejected because gauges are a separate operational entity with their own lifecycle.
- Use a single table without a type lookup: rejected because the backlog explicitly asks for both a gauge table and a gauge type table.
- Introduce a generic asset-management abstraction: rejected because the scope is too broad for the current backlog item and would add unnecessary indirection.

## Implementation Details
- Added `ITHTestGaugeType` with a unique name and a one-to-many relationship to gauges.
- Added `ITHTestGauge` with type, name, serial number, calibration due date, and certification due date fields.
- Registered both models in `src/ith_webapp/models/__init__.py` so metadata creation includes the new tables.
- Added a dedicated `/ith-test-gauges` blueprint with list, detail, create, edit, and delete routes.
- Added list, detail, and form templates plus navigation from the shared layout.
- Added an Alembic migration to create both tables.

## Validation
- `pytest -q tests/unit/test_ith_test_gauge_model.py` passes.
- `pytest -q tests/unit/test_ith_test_gauge_views.py` covers list, detail, create, edit, and delete routes.
- The new model and migration follow the existing SQLAlchemy/Alembic conventions used elsewhere in the app.

## Consequences
- Gauge tracking now has first-class persistence and CRUD screens.
- The schema gains one lookup table and one operational table.
- Future work can add more gauge-specific fields without changing the surrounding pattern.

## Monitoring & Rollback
- Review after the next calibration-related backlog item lands.
- Rollback: remove the blueprint, templates, migration, model registration, and tests if the feature is superseded.

## References
- F-034 in `prd.json`
- `src/ith_webapp/models/ith_test_gauge.py`
- `src/ith_webapp/models/ith_test_gauge_type.py`
- `src/ith_webapp/views/ith_test_gauges.py`
- `migrations/versions/2026_04_19_08_add_ith_test_gauge_tables.py`
- `tests/unit/test_ith_test_gauge_model.py`
- `tests/unit/test_ith_test_gauge_views.py`
