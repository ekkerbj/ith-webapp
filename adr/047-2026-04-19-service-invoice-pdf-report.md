# ADR 047: Service Invoice PDF Report

## Metadata
- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-047 PDF output, invoice-style layout, Avatax variant support, minimal dependency footprint
- **Tags**: reports, PDF, invoice, Flask

## Decision
Implement the Service Invoice report as a Flask blueprint route backed by the in-repo PDF writer. The report renders fab number lines, accessories, sales lines, and a tax variant label, with a dedicated Avatax variant when requested.

## Context
The backlog requires a service invoice PDF that mirrors the legacy Access outputs. The application already has a small deterministic PDF writer for quote-style reports, and the invoice layout is narrow enough to avoid a new rendering dependency.

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
- Add `build_service_invoice_pdf(session, service_id, region=None, variant=None)` to `src/ith_webapp/reports.py`.
- Query `Service` and related `ServiceSub` rows to build the invoice body.
- Render fab number lines, accessories, and sales lines using the existing PDF writer helpers.
- Include a tax variant line that resolves to `Avatax` when `variant=avatax`.
- Expose `/reports/service-invoice/<service_id>` as a PDF response.

## Validation
- Added unit tests that create a service with fab, accessory, and sales lines and assert the generated PDF contains the expected sections, region label, and Avatax variant label.
- Ran the full pytest suite successfully.

## Consequences
- The report is deterministic and easy to test.
- No new runtime dependency is required.
- Future invoice-style reports can reuse the same writer, but highly styled layouts may eventually justify a richer renderer.

## Monitoring & Rollback
- **Review date**: 2026-05-01
- **Success metric**: the report route continues to return valid PDF bytes for service invoices.
- **Rollback strategy**: remove the report function and route if a different rendering approach is adopted later.

## References
- `prd.json` F-047
- `src/ith_webapp/reports.py`
- `src/ith_webapp/app.py`
- `tests/unit/test_service_invoice_report.py`
