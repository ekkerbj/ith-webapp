# ADR 055: SAP Financial Summaries as Server-Rendered HTML

## Metadata
- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-055 backlog item, deterministic HTML output, reuse of the existing reports blueprint, no SAP connector implementation yet
- **Tags**: reports, html, sap, summaries, financials

## Decision
Implement the SAP financial summary surface as server-rendered HTML on the existing reports blueprint. The report page renders invoice and credit memo summaries with breakdowns by industry, item, salesperson, and state.

## Context
F-055 replaces legacy Access summary reports with browser-rendered tables. The codebase already has a dedicated reports blueprint and a pattern for rendering deterministic server-side reports. SAP connector work is still abstracted behind repository interfaces, so the financial summary report needs to accept a narrow repository contract rather than depend on a live SAP connection.

## Alternatives Considered

### Generate PDFs for the summaries
- **Pros**: consistent with other report exports.
- **Cons**: adds rendering complexity for tabular data that is easier to inspect in HTML.
- **Rejected**: the backlog explicitly calls for HTML tables.

### Build a separate reporting service
- **Pros**: could isolate SAP report concerns.
- **Cons**: more moving parts and a larger deployment surface.
- **Rejected**: unnecessary for a deterministic table-based report.

### Add a direct SAP connector now
- **Pros**: could read live SAP data.
- **Cons**: couples the report to an unfinished integration boundary.
- **Rejected**: the repository abstraction from F-038 is the intended seam.

## Implementation Details
- Added `/reports/sap/financial-summaries` with optional document-type and breakdown selectors.
- The route reads a repository from `SAP_FINANCIAL_SUMMARY_REPOSITORY`.
- The repository is expected to expose `list_invoice_summaries()` and `list_credit_memo_summaries()`.
- The page renders grouped HTML tables with count and total columns for each breakdown.
- The grouping logic is local and deterministic so the HTML remains easy to test.

## Validation
- Added a unit test covering the HTML report surface with representative invoice and credit memo rows.
- Ran the full pytest suite successfully.

## Consequences
- The report surface is browser-friendly and easy to extend with additional breakdowns.
- The report remains decoupled from any specific SAP transport.
- Future adapter work only needs to satisfy the repository contract.

## Monitoring & Rollback
- **Review date**: 2026-05-01
- **Success metric**: the HTML report continues to render the expected summary tables for representative SAP data.
- **Rollback strategy**: remove the route, helper functions, test, and repository configuration key if a different reporting approach is adopted.

## References
- `prd.json` F-055
- `src/ith_webapp/reports.py`
- `tests/unit/test_sap_financial_summary_report.py`
- `src/ith_webapp/repositories/sap_repository.py`
