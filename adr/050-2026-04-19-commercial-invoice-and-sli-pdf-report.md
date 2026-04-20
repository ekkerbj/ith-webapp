# ADR 050: Commercial Invoice and SLI PDF Report

## Metadata
- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-050 PDF output, international shipping documents, deterministic server rendering, minimal dependency footprint
- **Tags**: reports, PDF, commercial invoice, SLI, Flask

## Decision
Implement the Commercial Invoice and Shipper's Letter of Instruction report as a Flask blueprint route backed by the in-repo PDF writer. The report renders a commercial invoice header, a Shipper's Letter of Instruction section, and export compliance fields from packing list sub-items.

## Context
F-050 requires shipping documents that can be generated deterministically from the existing packing list data model. The current schema already stores export compliance data on `PackingListSub`, so the report can be delivered without introducing a new renderer or additional tables.

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
- Add `build_commercial_invoice_and_sli_pdf(session, packing_list_id)` to `src/ith_webapp/reports.py`.
- Query `PackingList` and related `PackingListSub` rows to build the shipping document body.
- Render both document headings plus each line item's compliance fields.
- Expose `/reports/commercial-invoice-and-sli/<packing_list_id>` as a PDF response.
- Reuse the existing PDF pagination and writer helpers.

## Validation
- Added a unit test that creates a packing list with compliance rows and asserts the generated PDF contains the expected report sections and field values.
- Ran the full pytest suite successfully.

## Consequences
- The report is deterministic and easy to test.
- No new runtime dependency is required.
- Future shipping document reports can reuse the same writer.

## Monitoring & Rollback
- **Review date**: 2026-05-01
- **Success metric**: the report route continues to return valid PDF bytes for commercial invoice and SLI documents.
- **Rollback strategy**: remove the report function and route if a different rendering approach is adopted later.

## References
- `prd.json` F-050
- `src/ith_webapp/reports.py`
- `src/ith_webapp/models/packing_list.py`
- `src/ith_webapp/models/packing_list_sub.py`
- `tests/unit/test_commercial_invoice_report.py`
