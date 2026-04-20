# ADR 072: Item Usage Analytics HTML Report

## Metadata
- Date: 2026-04-20
- Status: Accepted
- Authors: The AI
- Drivers: F-072 backlog item, deterministic browser-readable analytics, reuse of the reports blueprint, narrow SAP repository seam
- Tags: reports, html, sap, analytics, items

## Decision
Implement item usage analytics as a server-rendered HTML report on the existing reports blueprint. The report renders 1-year, 2-year, and 3-year item usage sections using a repository contract that returns item-level quantities for credit memos, invoices, production, and assembly/disassembly.

## Context
The backlog calls for item consumption analytics derived from SAP data over multiple lookback windows. The project already uses HTML reports for other SAP summaries, and the SAP connector is still abstracted behind repository interfaces. A server-rendered report keeps the analytics deterministic and easy to test without introducing a separate reporting service.

## Alternatives Considered
- PDF output: rejected because tabular analytics are easier to scan and compare in HTML.
- A separate analytics service: rejected because the current feature fits the existing Flask reports blueprint.
- Direct SAP calls inside the view: rejected because it would bypass the repository seam and make the report harder to test.

## Implementation Details
- Added `SapItemUsageRecord` and `SapItemUsageRepository` to `src/ith_webapp/repositories/sap_repository.py`.
- Added `/reports/sap/item-usage` to `src/ith_webapp/reports.py`.
- The view requests item usage data for 1, 2, and 3 years and renders a table per period.
- Rows are sorted by item code and name to keep the output deterministic.

## Validation
- Added unit coverage for the HTML report and the repository protocol.
- Ran `pytest -q` successfully.

## Consequences
- Item usage analytics now have a stable web surface.
- SAP integration work can target a narrow protocol instead of a concrete connector.
- The report is easy to extend with more periods or additional quantity columns later.

## Monitoring & Rollback
- Review after the first real SAP adapter is wired to confirm the protocol still matches the available query shape.
- Roll back by removing the route, template helper, record type, protocol, and test coverage if a different analytics surface is chosen.

## References
- F-072 in `prd.json`
- `src/ith_webapp/reports.py`
- `src/ith_webapp/repositories/sap_repository.py`
- `tests/unit/test_sap_item_usage_report.py`
- `tests/unit/test_sap_repository_interfaces.py`
