# ADR 074: Repair Time Analysis HTML Report

## Metadata
- Date: 2026-04-20
- Status: Accepted
- Authors: The AI
- Drivers: F-074 backlog item, deterministic HTML reporting, reuse of existing service-time data, no new persistence model
- Tags: reports, html, service, time-tracking

## Decision
Implement the repair time analysis as a server-rendered HTML report on the existing reports blueprint. The report groups `ServiceTime` rows by service and technician so the page shows time spent per service/technician combination.

## Context
The backlog requires an HTML report for analyzing repair labor time. The application already stores service time entries in `service_time`, links them to `service` and `customer`, and uses `render_template_string` for other deterministic report pages. A new reporting subsystem or persisted summary table would duplicate source data.

## Alternatives Considered
- **PDF output**: rejected because the backlog explicitly calls for HTML and the data is easier to inspect in a browser.
- **Raw per-entry listing**: rejected because the report goal is analysis, not just history, and grouped rows are more useful.
- **Precomputed summary tables**: rejected because existing relational data is sufficient and the report should stay read-only.

## Implementation Details
- Added `/reports/repair-time-analysis` to the reports blueprint.
- Added a helper that joins `ServiceTime`, `Service`, and `Customer`, then aggregates rows by `(service_id, technician)`.
- The HTML view renders customer, service ID, technician, entry count, total hours, and total labor for each grouped row.

## Validation
- Added a unit test that creates multiple time entries and verifies grouped totals in the HTML response.
- Ran the full pytest suite successfully.

## Consequences
- The report now provides a browser-friendly labor analysis without introducing new tables.
- Grouping by service and technician keeps the output focused on the operational question the report answers.
- The report depends on existing service/customer joins, so schema changes there would affect the output.

## Monitoring & Rollback
- Review after the next service-time related change to confirm the grouping still matches the legacy Access report intent.
- Roll back by removing the route, helper, template, tests, and this ADR if a different report shape is required.

## References
- `prd.json` F-074
- `src/ith_webapp/reports.py`
- `src/ith_webapp/models/service_time.py`
- `tests/unit/test_open_repair_list_and_shop_data_report.py`
