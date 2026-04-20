# ADR 035: Wind and Gas Turbine Site Tracking

- Date: 2026-04-19
- Status: Accepted
- Authors: The AI
- Drivers: F-035 backlog item, need for turbine installation site records, need for sales-pipeline lead tracking, consistency with existing Flask/SQLAlchemy CRUD patterns
- Tags: site-tracking, wind, gas, leads, CRUD, migration, templates
- Supersedes: None
- Superseded By: None

## Decision

Add dedicated SQLAlchemy models and CRUD screens for `sites_gas_turbine`, `sites_wind_turbine`, `sites_wind_gas`, `wind_turbine_leads`, and `wind_turbine_leads_details`.

## Context

F-035 requires persistence for turbine installation site tracking and wind turbine lead management. The application already favors small feature-specific tables, Flask blueprints, and server-rendered Jinja templates, so the new work should extend that pattern instead of introducing a generic admin framework.

## Alternatives Considered

- Reuse an existing table for all turbine records: rejected because installation sites and sales leads have different lifecycles and fields.
- Model all records in one polymorphic table: rejected because it would obscure the separate site and lead workflows.
- Add only schema without CRUD views: rejected because the backlog explicitly requires UI support.

## Implementation Details

- Added models for gas, wind, and hybrid site tracking plus wind turbine lead header/detail records.
- Added a relationship from `WindTurbineLead` to `WindTurbineLeadDetail` so lead follow-up notes stay attached to the lead.
- Added a single reusable CRUD view module with one blueprint per resource and shared list/detail/form templates.
- Registered the new blueprints in `create_app()`.
- Added an Alembic migration to create all five tables.

## Validation

- `pytest -q tests/unit/test_wind_turbine_tracking_models.py`
- `pytest -q tests/unit/test_wind_turbine_tracking_views.py`
- `pytest -q`

## Consequences

- Turbine site and lead data can now be created, viewed, edited, and deleted through the web app.
- The new generic CRUD templates reduce duplication across the feature.
- Adds a modest amount of schema and route surface area.

## Monitoring & Rollback

- Review after the next turbine-related backlog item lands.
- Rollback by removing the migration, models, blueprint registration, templates, tests, and ADR if the feature is superseded.

## References

- `prd.json` F-035
- `src/ith_webapp/models/site_gas_turbine.py`
- `src/ith_webapp/models/site_wind_turbine.py`
- `src/ith_webapp/models/site_wind_gas.py`
- `src/ith_webapp/models/wind_turbine_lead.py`
- `src/ith_webapp/models/wind_turbine_lead_detail.py`
- `src/ith_webapp/views/wind_turbine_tracking.py`
- `migrations/versions/2026_04_19_09_add_wind_turbine_tracking_tables.py`
