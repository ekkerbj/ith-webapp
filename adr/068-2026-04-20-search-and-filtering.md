# ADR 068: Search and Filtering

## Metadata
- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: Copilot
- **Drivers**: F-068, Access-style filtering, route discoverability, searchability of master data
- **Tags**: search, filtering, customers, parts, packing-lists, field-services

## Decision
Add query-string filtering to the customer, field service, parts, and packing list index views, and expose the new index routes from the switchboard. Extend `PackingList` with nullable customer/date header fields so packing lists can participate in the same search pattern.

## Context
The backlog item calls for global search and per-entity filtering that mirrors Access form filters. The application already had list views for customers and field services, but parts and packing lists did not have searchable index pages. Packing lists also lacked header fields that could be filtered by customer or date.

## Alternatives Considered
- **Single global search page only**: Rejected because the existing workflow is list-driven and users need per-entity browsing as well as search.
- **Leave parts and packing lists without index pages**: Rejected because the backlog explicitly names them as searchable entities.
- **Persist all filtering state in the database layer**: Rejected because the scope is simple text filtering and the list pages can filter safely at the view layer for now.

## Implementation Details
- Customer list now filters by `q` against customer name and card code.
- Field service list now filters by `q` against service ID, customer name, and status name.
- Parts gained a new `/parts/` index route that filters by item code or description.
- Packing lists gained a new `/packing-lists/` index route that filters by customer name or packing date.
- `PackingList` now includes nullable `customer_name` and `packing_date` columns, plus a migration to persist them.
- The switchboard now links to the parts and packing list index routes.

## Validation
- Added regression tests for customer, field service, parts, packing list model, and packing list index filtering.
- Ran the full pytest suite successfully: 152 passed.

## Consequences
- Master data is easier to browse without leaving the server-rendered UI.
- Packing lists now have minimal searchable header metadata.
- Filtering logic is simple and readable, but still lives in the views instead of a shared search service.

## Monitoring & Rollback
- **Review date**: 2026-05-04
- **Success metric**: users can narrow each master list with a query string and reach the relevant index pages from the switchboard.
- **Rollback strategy**: remove the new index routes, query filtering, packing list header fields, and migration if the workflow needs a different search model.

## References
- `prd.json` F-068
- `src/ith_webapp/views/customers.py`
- `src/ith_webapp/views/field_service.py`
- `src/ith_webapp/views/parts.py`
- `src/ith_webapp/views/packing_list_workflow.py`
- `src/ith_webapp/models/packing_list.py`
- `migrations/versions/2026_04_20_01_add_packing_list_search_fields.py`
- `tests/unit/test_customer_views.py`
- `tests/unit/test_field_service_views.py`
- `tests/unit/test_parts_views.py`
- `tests/unit/test_packing_list_model.py`
- `tests/unit/test_packing_list_workflow.py`
