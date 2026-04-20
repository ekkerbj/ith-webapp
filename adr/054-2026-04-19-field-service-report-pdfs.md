# ADR 054: Field Service Report PDFs

- Date: 2026-04-19
- Status: Accepted
- Authors: The AI
- Drivers: F-054 backlog item, consistent PDF report routing, customer-facing timesheet output
- Tags: reports, pdf, field-service, timesheet
- Supersedes: None
- Superseded By: None

## Decision

Implement three field service PDF endpoints: a field service report, a field service summary, and a field service timesheet with a customer-facing variant.

## Context

F-054 requires the field service reporting surface to cover the main report, a shorter summary, and a timesheet-style export. The existing codebase keeps PDF generation in `src/ith_webapp/reports.py`, with route handlers delegating to builder functions and tests validating the rendered bytes.

## Alternatives Considered

- One generic report with a query-string mode: rejected because the other report endpoints in the codebase use dedicated routes for distinct documents.
- Reusing the service-measurements report shape: rejected because field service data is keyed by `FieldService` and its related `ServiceTime` entries need separate presentation.

## Implementation Details

- Added `build_field_service_report_pdf()`, `build_field_service_summary_pdf()`, and `build_field_service_timesheet_pdf()`.
- The report data loads `FieldService` records and joins `ServiceTime` through `Service.customer_id`, since field service records are customer-linked and service time entries live under service orders.
- Added `/reports/field-service/<id>`, `/reports/field-service-summary/<id>`, and `/reports/field-service-timesheet/<id>` routes.
- The timesheet route accepts `customer_facing=1|true|yes` and switches to a customer-facing title and reduced detail.

## Validation

- Unit tests cover PDF generation and all three routes.
- Full test suite passes after the change.

## Consequences

- Field service reporting is now available as PDF output without introducing a new report subsystem.
- The customer-facing timesheet variant is supported without duplicating the underlying query logic.
- The report layer now depends on a customer-to-service join to reach time entries.

## Monitoring & Rollback

- Review: 2026-05-01
- Success: field service PDFs render for records with and without time entries.
- Rollback: remove the new report helpers and routes, then revert the ADR and backlog update.

## References

- prd.json F-054
- src/ith_webapp/reports.py
- tests/unit/test_field_service_report.py
- src/ith_webapp/models/field_service.py
- src/ith_webapp/models/service_time.py
