# ADR 045: Service Multi Quote PDF Report

## Metadata
- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-045 PDF output, multi-section quote layout, regional variants, minimal dependency footprint
- **Tags**: reports, PDF, quotes, Flask

## Decision
Implement the Service Multi Quote report as a Flask blueprint route backed by a small in-repo PDF writer. The report renders fab number line items, accessories, sales items, a signature block, and regional labels for Brazil and Mexico.

## Context
The backlog requires a Service Multi Quote PDF that mirrors the legacy Access output. The application did not already have a document-generation stack, and the report only needs a narrow, predictable layout. Adding a large third-party rendering dependency would increase maintenance and deployment cost for a single report.

## Alternatives Considered

### Add a third-party PDF renderer
- **Pros**: richer layout features, less low-level PDF code.
- **Cons**: new dependency, more packaging risk, and more surface area than needed for the current report.
- **Rejected**: the report requirements are simple enough for a small custom writer.

### Generate HTML and print it as PDF in the browser
- **Pros**: fewer server-side PDF details.
- **Cons**: inconsistent output, weaker testability, and an extra client-side dependency.
- **Rejected**: the report should be server-rendered and deterministic.

## Implementation Details
- Add `ith_webapp.reports` with `build_service_multi_quote_pdf(session, service_id, region=None)`.
- Query the `Service` and related `ServiceSub` rows from the database.
- Group rows into fab number line items, accessories, and sales items by `item_type`.
- Render a multi-page PDF with a tiny in-repo writer using Helvetica and plain text streams.
- Expose `/reports/service-multi-quote/<service_id>` as a PDF response.
- Register the reports blueprint in `create_app()`.

## Validation
- Added a unit test that creates a service with fab, accessory, and sales line items and asserts the PDF bytes include the expected report sections and variant label.
- Ran the full pytest suite successfully.

## Consequences
- The report is deterministic and easy to test.
- The implementation avoids a new runtime dependency.
- Future PDF reports can reuse the same writer, but complex layouts may eventually justify a richer rendering library.

## Monitoring & Rollback
- **Review date**: 2026-05-01
- **Success metric**: the report route continues to return valid PDF bytes for service quotes.
- **Rollback strategy**: remove the blueprint and `ith_webapp.reports` module if a different rendering approach is adopted later.

## References
- `prd.json` F-045
- `src/ith_webapp/reports.py`
- `src/ith_webapp/app.py`
- `tests/unit/test_service_multi_quote_report.py`
