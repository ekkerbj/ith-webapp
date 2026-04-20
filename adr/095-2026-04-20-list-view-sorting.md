# ADR 095: List View Sorting

## Metadata
- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: Copilot
- **Drivers**: F-095, table usability, shared CRUD list consistency, URL-preserved state
- **Tags**: sorting, list-views, crud, ui

## Decision
Add shared server-side column sorting for the server-rendered list views, with clickable headers that toggle ascending and descending order while preserving existing query-string filters and pagination state.

## Context
The application already had a shared list template and shared pagination logic, but the list pages always rendered in their default database order. The backlog requires sortable table headers across the list views, and the sort state must survive paging and filtering so users can refine result sets without losing context.

## Alternatives Considered
- **Client-side sorting only**: Rejected because it would sort only the current page slice and would not work consistently with server-side pagination.
- **Per-view ad hoc header links**: Rejected because it would duplicate URL-building and sort toggling logic in every list route.
- **Leave list ordering fixed**: Rejected because it does not satisfy the backlog item or the expected table interaction model.

## Implementation Details
- Added `ith_webapp.services.table_sorting` with helpers to apply sort expressions to SQLAlchemy queries and to build header-link metadata.
- Updated `crud/list.html` to render sortable column links and show the active direction.
- Wired the shared CRUD-style list routes to pass sortable column metadata and to order their queries with model-specific sort maps.
- Preserved `q` and any other list filters in generated sort links and in pagination URLs.

## Validation
- Added regression coverage for sorted customer lists.
- Ran the full pytest suite successfully: 201 passed.

## Consequences
- Users can now sort list views without leaving the current server-rendered flow.
- Sort state now stays in the URL, which makes paging and sharing links more predictable.
- Each list route now owns a small sort map, but the link-generation and direction-toggle behavior is centralized.

## Monitoring & Rollback
- **Review date**: 2026-05-04
- **Success metric**: list headers toggle correctly and paging links preserve active sort/filter parameters.
- **Rollback strategy**: remove the shared sorting helper, revert the list routes to fixed ordering, and restore the old list template header rendering.

## References
- `prd.json` F-095
- `src/ith_webapp/services/table_sorting.py`
- `src/ith_webapp/services/pagination.py`
- `src/ith_webapp/templates/crud/list.html`
- `src/ith_webapp/views/customers.py`
- `src/ith_webapp/views/parts.py`
- `src/ith_webapp/views/field_service.py`
- `src/ith_webapp/views/consignment_list.py`
- `src/ith_webapp/views/rentals.py`
- `src/ith_webapp/views/demo_contracts.py`
- `src/ith_webapp/views/order_confirmations.py`
- `src/ith_webapp/views/warranty_claims.py`
- `src/ith_webapp/views/ith_test_gauges.py`
- `src/ith_webapp/views/packing_list_workflow.py`
- `src/ith_webapp/views/projects.py`
- `src/ith_webapp/views/wind_turbine_tracking.py`
- `tests/unit/test_customer_views.py`
