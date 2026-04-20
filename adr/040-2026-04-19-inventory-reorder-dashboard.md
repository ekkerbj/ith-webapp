# ADR 040: Inventory Reorder Dashboard

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI
- Drivers: F-040 requirement for reorder calculation and dashboard visibility
- Tags: inventory, SAP, dashboard, calculation

## Decision
Add an inventory reorder dashboard route that calculates reorder quantity from SAP warehouse stock using `min_stock - on_hand + committed - on_order`, and display only items with a positive reorder quantity.

## Context
The backlog requires a web dashboard for items that need replenishment. The SAP warehouse repository already exposes stock records, but it does not enumerate items, so the dashboard must operate from a configured list of item codes and warehouse code.

## Alternatives Considered
- Persist reorder rules in a database table: rejected because the immediate requirement is a read-only dashboard, not admin-managed inventory configuration.
- Compute reorder quantities inside the repository: rejected because calculation is application policy, not data access.
- Render all stock rows regardless of deficit: rejected because the dashboard is intended to highlight items needing reorder.

## Implementation Details
- Add a route at `/inventory/reorder`.
- Read `INVENTORY_REORDER_REPOSITORY`, `INVENTORY_REORDER_WAREHOUSE_CODE`, and `INVENTORY_REORDER_ITEM_CODES` from app config.
- Calculate reorder quantity as `min_stock - on_hand + committed - on_order`.
- Filter out rows where the result is not positive.
- Render a simple HTML table with the item code and reorder quantity.

## Validation
- Added a unit test covering positive reorder output and negative reorder filtering.
- Full pytest suite passes.

## Consequences
- The reorder formula is centralized and testable.
- The dashboard stays decoupled from SAP enumeration details.
- The view depends on app configuration for item selection.

## Monitoring & Rollback
- Review: 2026-05-01
- Success metric: reorder dashboard remains stable as SAP stock integrations evolve.
- Rollback: remove the route and helper logic; no schema changes are required.

## References
- F-040 in `prd.json`
- `src/ith_webapp/repositories/sap_repository.py`
- `src/ith_webapp/app.py`
