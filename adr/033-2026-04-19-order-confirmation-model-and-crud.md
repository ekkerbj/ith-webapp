# ADR 033: Order Confirmation Model and CRUD

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI, project team
- Drivers: F-033 backlog item, consistency with existing Flask/SQLAlchemy CRUD resources, lightweight schema modeling
- Tags: order confirmation, model, migration, Flask, CRUD, customer

## Decision
Implement a dedicated `OrderConfirmation` SQLAlchemy model, an Alembic migration for the `order_confirmation` table, and a Flask CRUD blueprint under `/order-confirmations`.

## Context
F-033 requires order confirmation records. The codebase already favors one table per business record, one blueprint per resource, and server-rendered Jinja2 pages. A dedicated resource keeps order confirmations isolated from unrelated customer or service records.

## Alternatives Considered
- Store confirmation data on `Customer`: rejected because confirmations are event records with their own lifecycle.
- Reuse `CustomerCommunicationLog`: rejected because confirmations are a distinct operational record and should remain queryable on their own.
- Skip the table and use only views: rejected because the backlog explicitly requires an `order_confirmation` table.

## Implementation Details
- Added `OrderConfirmation` with `order_confirmation_id`, `customer_id`, `order_number`, `notes`, and `created_at`.
- Registered the model in `src/ith_webapp/models/__init__.py` so metadata creation includes the table.
- Added an `order_confirmations` blueprint with list, detail, create, edit, and delete routes.
- Added list, detail, and form templates and linked the resource in the main navigation.
- Added an Alembic migration to create `order_confirmation`.

## Validation
- `pytest -q tests/unit/test_order_confirmation_model.py tests/unit/test_order_confirmation_views.py tests/unit/test_app.py` passes.
- `pytest -q` passes for the full repository.

## Consequences
- Order confirmations are now first-class records instead of ad hoc notes.
- The app gains another CRUD surface and another migration to maintain.
- The schema stays aligned with the lightweight resource pattern used by the rest of the app.

## Monitoring & Rollback
- Review after the next customer-order workflow feature lands.
- Rollback: remove the blueprint, templates, migration, model registration, and tests if the resource is superseded.

## References
- F-033 in `prd.json`
- `src/ith_webapp/models/order_confirmation.py`
- `src/ith_webapp/views/order_confirmations.py`
- `migrations/versions/2026_04_19_07_add_order_confirmation_table.py`
- `tests/unit/test_order_confirmation_model.py`
- `tests/unit/test_order_confirmation_views.py`
