# ADR 046: Basic Quote PDF Report

## Metadata
- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-046 PDF output, BOM-driven quote layout, regional variants, minimal dependency footprint
- **Tags**: reports, PDF, quotes, Flask

## Decision
Implement the Basic Quote report as a Flask blueprint route backed by the existing in-repo PDF writer. The report renders a BOM section plus static Terms and Conditions, Why ITH, and Credit References pages, with regional labels for Brazil and Mexico.

## Context
The backlog requires a Basic Quote PDF that mirrors the legacy Access output. The application already uses a small deterministic PDF writer for quote-style reports, and the Basic Quote layout is predictable enough to avoid a third-party rendering dependency.

## Alternatives Considered

### Add a third-party PDF renderer
- **Pros**: richer layout features and less low-level PDF code.
- **Cons**: new dependency, extra packaging risk, and more maintenance surface.
- **Rejected**: unnecessary for the current report scope.

### Generate HTML and print it as PDF in the browser
- **Pros**: simpler server code.
- **Cons**: inconsistent output and weaker testability.
- **Rejected**: the report should stay server-rendered and deterministic.

## Implementation Details
- Add `build_basic_quote_pdf(session, parts_list_id, region=None)` to `src/ith_webapp/reports.py`.
- Query `PartsList`, `PartsSub`, and related `Part` rows to render the BOM.
- Render static sections for Terms and Conditions, Why ITH, and Credit References.
- Expose `/reports/basic-quote/<parts_list_id>` as a PDF response.
- Reuse the existing PDF pagination and writer helpers.

## Validation
- Added unit tests that create a BOM and assert the generated PDF contains the expected report sections, regional labels, and route response headers.
- Ran the full pytest suite successfully.

## Consequences
- The report is deterministic and easy to test.
- No new runtime dependency is required.
- Future PDF reports can reuse the same writer, but highly styled layouts may eventually justify a richer renderer.

## Monitoring & Rollback
- **Review date**: 2026-05-01
- **Success metric**: the report route continues to return valid PDF bytes for basic quotes.
- **Rollback strategy**: remove the report function and route if a different rendering approach is adopted later.

## References
- `prd.json` F-046
- `src/ith_webapp/reports.py`
- `src/ith_webapp/app.py`
- `tests/unit/test_basic_quote_report.py`
