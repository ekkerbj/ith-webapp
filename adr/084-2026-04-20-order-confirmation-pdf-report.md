# ADR 084: Order Confirmation PDF Report

## Metadata

- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: Development team
- **Drivers**: F-084 backlog item, Access report parity, printable order confirmation output, reuse of existing PDF infrastructure
- **Tags**: architecture, reporting, pdf, order-confirmation
- **Supersedes**: None
- **Superseded By**: None

## Decision

Add a PDF report endpoint in `src/ith_webapp/reports.py` for `OrderConfirmation` records at `/reports/order-confirmation/<id>`.

## Context

F-084 requires a printable order confirmation report. The application already stores the underlying data in `OrderConfirmation` and already uses a lightweight internal PDF builder for other text-first reports, so the new report should follow the same pattern.

The report only needs the record header fields and customer context; it does not require a new template system or additional persistence.

## Alternatives Considered

### Render the confirmation as HTML only

- **Rejected**: the backlog explicitly calls for PDF output.
- **Rejected**: HTML would not match the printable legacy workflow.

### Introduce a separate PDF library or template engine

- **Rejected**: unnecessary complexity for a small text-heavy document.
- **Rejected**: the existing PDF builder already matches the project pattern.

### Fold the confirmation into the CRUD detail page only

- **Rejected**: the report needs its own export path and inline filename.

## Implementation Details

- Added `build_order_confirmation_pdf(session, order_confirmation_id)` to load the record and build a text-first PDF.
- The report includes customer name, card code, order number, created timestamp, notes, and signature lines.
- Added a `/reports/order-confirmation/<id>` route that returns `application/pdf` with an inline filename.
- Added unit coverage for the PDF route and content.

## Validation

- Added unit coverage for PDF content and route behavior.
- Full test suite passes after the change.

## Consequences

### Positive

- Order confirmations are now available as printable PDFs.
- The implementation reuses the same report infrastructure as other documents.

### Negative

- The report is text-based and does not reproduce richer Access layout details.

### Neutral

- The report module gains one builder function and one route.

## Monitoring & Rollback

- **Review date**: After the next order workflow report change
- **Success metrics**: the PDF renders for existing order confirmation records and includes the expected record details
- **Rollback strategy**: remove the builder, route, related tests, and this ADR if the report surface changes

## References

- `prd.json` F-084
- `src/ith_webapp/reports.py`
- `src/ith_webapp/models/order_confirmation.py`
- `tests/unit/test_order_confirmation_views.py`
