# ADR 026: Consignment List Model and CRUD Views

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI, project team
- Drivers: F-028 requirement for consignment inventory at customer sites
- Tags: consignment, model, migration, Flask, CRUD, customer, part

## Decision
Implement a dedicated `ConsignmentList` SQLAlchemy model, an Alembic migration for the `consignment_list` table, and a Flask CRUD blueprint under `/consignment-lists`.

## Context
F-028 requires tracking inventory held at customer sites. The existing codebase already has `Customer` and `Part` master records, so the consignment record can be modeled as a join-like resource with a quantity attached. A standalone resource keeps the UI and schema aligned with the backlog item instead of folding the data into an unrelated aggregate.

## Alternatives Considered
- Embed consignment rows under Customer only: Rejected because the record also needs a first-class part reference.
- Embed consignment rows under Part only: Rejected because the operational context is the customer site.
- Reuse packing list tables: Rejected because packing and consignment represent different workflows and lifecycle rules.

## Implementation Details
- Added `ConsignmentList` with `consignment_list_id`, `customer_id`, `part_id`, and `quantity`.
- Added foreign keys to `customer.customer_id` and `part.part_id`.
- Registered the model in `src/ith_webapp/models/__init__.py` so metadata creation includes the table.
- Added a `consignment_list` blueprint with list, detail, create, edit, and delete routes.
- Added templates for the list, detail, and form views.

## Validation
- `pytest -q` passes.
- Unit coverage verifies list, detail, create, edit, and delete flows for the resource.

## Consequences
- Consignment inventory can now be stored and edited as a dedicated resource.
- The app gains one more blueprint and one more table in the schema.
- The model remains simple, but future validation may be needed if quantity or foreign-key constraints become stricter.

## Monitoring & Rollback
- Review after the next customer/parts inventory item lands.
- Rollback: remove the blueprint, templates, migration, and model registration if the resource is superseded.

## References
- F-028 in `prd.json`
- `src/ith_webapp/models/consignment_list.py`
- `src/ith_webapp/views/consignment_list.py`
- `tests/unit/test_consignment_list_views.py`
