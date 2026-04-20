# ADR 098: CSV and Excel Exports for List Views

## Metadata
- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-098, list-view export, CSV download, Excel-compatible download, shared list UI
- **Tags**: export, csv, excel, list-views, reports, ui

## Decision
Add CSV and Excel-compatible exports to the main list views by reusing the existing list query, sorting, and filtering behavior.

## Context
Users need a way to take the current filtered/sorted list data out of the application for offline analysis and spreadsheet workflows. The application already has a shared list rendering pattern, so the export behavior should follow the same data set rather than introducing a separate reporting path.

## Alternatives Considered
- **Add a dedicated export service layer per entity**: Rejected because it would duplicate list-query logic across views.
- **Introduce a third-party spreadsheet library**: Rejected because CSV and Excel-compatible tab-delimited output satisfy the need without adding dependencies.
- **Export only from one list view**: Rejected because the requirement covers the major operational list pages.

## Implementation Details
- Added `src/ith_webapp/services/list_exports.py` with a shared response builder for CSV and Excel-compatible exports.
- Added `?format=csv` and `?format=excel` handling to the Customers, Parts, Packing Lists, and Field Services list routes.
- CSV responses use `text/csv` and the current filtered/sorted rows.
- Excel responses use tab-delimited text with `application/vnd.ms-excel` so spreadsheets open the download without extra packages.
- Added export buttons to the shared `crud/list.html` template so the feature is discoverable from the main list pages.

## Validation
- Added regression coverage for CSV and Excel exports on the four major list views.
- Ran the full pytest suite successfully: 211 passed.

## Consequences
### Positive
- Users can export the same filtered/sorted list data they are already viewing.
- No new runtime dependency was required.
- The export behavior stays consistent across the major list pages.

### Negative
- The Excel export is compatibility-oriented rather than a native `.xlsx` workbook.
- Large exports still stream as full in-memory responses.

### Neutral
- The export format is controlled by a query parameter, so existing list URLs remain stable.

## Monitoring & Rollback
- **Review date**: 2026-05-04
- **Success metrics**: users can download CSV/Excel from the main list pages, and the exported rows match the on-screen filters and sort order.
- **Rollback strategy**: remove the format branch and export controls if spreadsheet downloads prove confusing or unreliable.

## References
- `prd.json` F-098
- `src/ith_webapp/services/list_exports.py`
- `src/ith_webapp/views/customers.py`
- `src/ith_webapp/views/parts.py`
- `src/ith_webapp/views/field_service.py`
- `src/ith_webapp/views/packing_list_workflow.py`
- `src/ith_webapp/templates/crud/list.html`
- `tests/unit/test_list_exports.py`
