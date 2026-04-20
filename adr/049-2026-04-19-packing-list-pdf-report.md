# ADR 049: Packing List PDF Report

## Metadata
- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-049 PDF output, shipment document layout, deterministic server rendering, minimal dependency footprint
- **Tags**: reports, PDF, packing list, Flask

## Decision
Implement the Packing List report as a Flask blueprint route backed by the in-repo PDF writer. The report renders a packing list header with line-item compliance fields for harm number, EECN, DDTC, COO, and in bond code.

## Context
The backlog requires a Packing List PDF that mirrors the legacy Access outputs. The current packing list schema is intentionally minimal, so the report must work with the existing `PackingList` and `PackingListSub` tables without introducing a new rendering dependency.

## Alternatives Considered

### Add a third-party PDF renderer
- **Pros**: richer layout features and less low-level PDF code.
- **Cons**: new dependency, packaging risk, and more maintenance surface.
- **Rejected**: unnecessary for the current report scope.

### Generate HTML and print it as PDF in the browser
- **Pros**: simpler server code.
- **Cons**: inconsistent output and weaker testability.
- **Rejected**: the report should stay server-rendered and deterministic.

## Implementation Details
- Add `build_packing_list_pdf(session, packing_list_id)` to `src/ith_webapp/reports.py`.
- Query `PackingList` and related `PackingListSub` rows to render the shipment document.
- Render the packing list id followed by each line item's export compliance fields.
- Expose `/reports/packing-list/<packing_list_id>` as a PDF response.
- Reuse the existing PDF pagination and writer helpers.

## Validation
- Added a unit test that creates a packing list with compliance rows and asserts the generated PDF contains the expected report sections and field values.
- Ran the full pytest suite successfully.

## Consequences
- The report is deterministic and easy to test.
- No new runtime dependency is required.
- Future shipment-style reports can reuse the same writer.

## Monitoring & Rollback
- **Review date**: 2026-05-01
- **Success metric**: the report route continues to return valid PDF bytes for packing lists.
- **Rollback strategy**: remove the report function and route if a different rendering approach is adopted later.

## References
- `prd.json` F-049
- `src/ith_webapp/reports.py`
- `src/ith_webapp/models/packing_list.py`
- `src/ith_webapp/models/packing_list_sub.py`
- `tests/unit/test_packing_list_report.py`
