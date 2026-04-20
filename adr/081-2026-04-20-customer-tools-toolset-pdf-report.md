# ADR 081: Customer Tools Toolset PDF Report

## Metadata

- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: Development team
- **Drivers**: Toolset report parity, customer tool traceability, PDF output consistency, minimal reuse of existing report infrastructure
- **Tags**: architecture, reporting, pdf, customer-tools, customer_tools_sub

## Decision

Add a PDF toolset detail report for `CustomerTools` records at `/reports/customer-tools/<id>` that includes the parent tool details and the component list from `CustomerToolsSub`.

## Context

The application already stored customer-owned tools and component rows in `customer_tools` and `customer_tools_sub`, and it already exposed a customer tools inventory HTML report. The product backlog also required a Toolset PDF matching two legacy Access reports.

The PDF report needed to fit the existing lightweight report infrastructure instead of introducing a separate rendering stack.

## Alternatives Considered

### Extend the inventory HTML report only

- **Rejected**: the backlog explicitly required PDF output.
- **Rejected**: HTML alone would not match the legacy report workflow.

### Introduce a templated PDF library

- **Rejected**: unnecessary complexity for a text-only report.
- **Rejected**: the existing internal PDF builder already handles the required output.

### Render the report as a single-page image

- **Rejected**: would reduce searchability and increase implementation cost.

## Implementation Details

- Added `build_customer_tools_pdf(session, customer_tools_id)` to `src/ith_webapp/reports.py`.
- The report loads the `CustomerTools` record, resolves its `Unit`, and queries ordered `CustomerToolsSub` rows.
- The PDF content includes customer name, serial number, fab number, model, unit, and a component list.
- Added a `/reports/customer-tools/<id>` route that returns `application/pdf` with an inline filename.

## Validation

- Added unit coverage for PDF content and route behavior.
- Full test suite passes after the change.

## Consequences

### Positive

- Toolset data is now available as a PDF report for the customer tools workflow.
- The implementation reuses the existing PDF generation helper and keeps the change small.

### Negative

- The report is text-based and does not reproduce any richer Access layout details.

### Neutral

- The HTML inventory report remains available separately.

## Monitoring & Rollback

- **Review date**: After the first production use of the Toolset report
- **Success metrics**: the report renders for existing customer tools records and includes component rows without errors
- **Rollback strategy**: remove the route and builder function, then revert the related tests and ADR if the report proves incorrect

## References

- `src/ith_webapp/reports.py`
- `src/ith_webapp/models/customer_tools.py`
- `tests/unit/test_customer_tools_report.py`
- `tests/unit/test_customer_tools_model.py`
