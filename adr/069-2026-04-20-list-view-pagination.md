# ADR 069: List View Pagination

## Metadata
- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: Copilot
- **Drivers**: F-069, large list usability, server-side paging, consistent browse behavior
- **Tags**: pagination, list-views, crud, ui

## Decision
Add shared server-side pagination for all list views, with a configurable default page size and next/previous navigation controls rendered in the shared list template.

## Context
The application had grown multiple server-rendered list pages that loaded entire result sets at once. That works for small tables, but it does not scale cleanly as the backlog expands the catalog and service records. The backlog specifically requires page navigation and configurable page size for list views, so the implementation needed to be consistent across the different blueprints.

## Alternatives Considered
- **Client-side paging only**: Rejected because it still fetches every record and does not help large tables.
- **Per-view bespoke pagination**: Rejected because it would duplicate paging math and fragment the UI.
- **Leave paging to the database layer only**: Rejected because the views still need shared navigation links and page-size controls.

## Implementation Details
- Added `ith_webapp.services.pagination.paginate_query()` to calculate page slices, total counts, and navigation URLs.
- Set a default `LIST_PAGE_SIZE` in `create_app()` so list views have a consistent baseline.
- Reworked list routes to pass paginated rows into `crud/list.html`.
- Updated the shared list template to render page counters, previous/next links, and a page-size form while preserving existing query-string filters.

## Validation
- Added regression coverage for customer list paging.
- Ran the full pytest suite successfully: 153 passed.

## Consequences
- Large list pages now load smaller result sets and are easier to browse.
- Navigation behavior is consistent across the server-rendered CRUD surfaces.
- The shared list template now carries a little more presentation logic, but the repeated paging code moved out of the views.

## Monitoring & Rollback
- **Review date**: 2026-05-04
- **Success metric**: list pages stay responsive and page changes preserve active filters.
- **Rollback strategy**: remove the shared pagination helper, revert the list routes to full result sets, and drop the pagination section from `crud/list.html`.

## References
- `prd.json` F-069
- `src/ith_webapp/services/pagination.py`
- `src/ith_webapp/templates/crud/list.html`
- `src/ith_webapp/views/customers.py`
- `src/ith_webapp/views/field_service.py`
- `src/ith_webapp/views/parts.py`
- `src/ith_webapp/views/consignment_list.py`
- `src/ith_webapp/views/projects.py`
- `src/ith_webapp/views/rentals.py`
- `src/ith_webapp/views/order_confirmations.py`
- `src/ith_webapp/views/warranty_claims.py`
- `src/ith_webapp/views/ith_test_gauges.py`
- `src/ith_webapp/views/demo_contracts.py`
- `src/ith_webapp/views/packing_list_workflow.py`
- `src/ith_webapp/views/wind_turbine_tracking.py`
- `tests/unit/test_pagination.py`
