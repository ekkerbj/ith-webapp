# ADR 082: Communication and Lead Letter PDF Reports

## Metadata
- Date: 2026-04-20
- Status: Accepted
- Authors: The AI, project team
- Drivers: F-082 backlog item, Access communication/CRM report parity, reuse of existing customer communication and wind turbine lead tables
- Tags: reporting, pdf, communication, leads, customer, wind-turbine
- Supersedes: None
- Superseded By: None

## Decision
Add three PDF report endpoints in `reports.py` for customer communications, wind turbine lead letters, and wind turbine lead follow-up letters.

## Context
F-082 requires report output for customer communication history and wind turbine lead correspondence. The codebase already uses lightweight PDF builders backed by SQLAlchemy queries, so these reports should follow the same pattern instead of introducing a new reporting framework.

## Alternatives Considered
- Render the reports as HTML only: rejected because the backlog explicitly calls for PDF output.
- Fold the reports into existing CRUD views: rejected because reports and data editing have separate workflows.
- Build a single generic correspondence report: rejected because the communication log, lead letter, and follow-up letter each have distinct record sources and templates.

## Implementation Details
- Added `build_customer_communication_report_pdf(session, customer_id)` to render a customer header plus ordered communication log entries.
- Added `build_wind_turbine_lead_letter_pdf(session, lead_id)` to render lead contact data, lead notes, and all follow-up notes.
- Added `build_wind_turbine_lead_follow_up_letter_pdf(session, lead_id, detail_id)` to render a single selected follow-up note.
- Added PDF routes:
  - `/reports/customer-communications/<customer_id>`
  - `/reports/wind-turbine-leads/<lead_id>/letter`
  - `/reports/wind-turbine-leads/<lead_id>/follow-up-letter/<detail_id>`
- Kept the implementation inside `src/ith_webapp/reports.py` to match the existing report module pattern.

## Validation
- `pytest -q tests/unit/test_communication_and_lead_letters_report.py`
- `pytest -q`

## Consequences
- Customer communication history can now be exported as a PDF report.
- Wind turbine lead correspondence now has printable letter formats.
- The report module gains a small amount of additional route and helper logic.

## Monitoring & Rollback
- Review after the next CRM/report backlog item lands.
- Rollback by removing the three helpers, three routes, their tests, and this ADR if the report surface is replaced.

## References
- `prd.json` F-082
- `src/ith_webapp/reports.py`
- `src/ith_webapp/models/customer_communication_log.py`
- `src/ith_webapp/models/wind_turbine_lead.py`
- `src/ith_webapp/models/wind_turbine_lead_detail.py`
- `tests/unit/test_communication_and_lead_letters_report.py`
