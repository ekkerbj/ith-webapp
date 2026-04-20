# ADR 053: Customer Reports as Server-Rendered HTML

## Metadata
- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-053 report coverage, deterministic output, minimal dependency footprint, reuse of existing Flask report blueprint
- **Tags**: reports, HTML, customers, Flask

## Decision
Implement the customer report suite as server-rendered HTML routes on the existing reports blueprint. The suite includes a customer detail report plus grouped views for region, responsibility, pricing, and tool inventory.

## Context
F-053 covers several legacy customer report variants. The application already has the needed customer, market, application, and tool data in SQLAlchemy models, so the reports can be generated deterministically without introducing a PDF renderer or separate reporting service.

## Alternatives Considered

### Generate PDFs for every customer report
- **Pros**: uniform output format.
- **Cons**: more rendering code and lower flexibility for tabular data.
- **Rejected**: the report set is primarily informational and fits HTML well.

### Add a third-party reporting engine
- **Pros**: richer formatting and export features.
- **Cons**: new dependency and packaging risk.
- **Rejected**: unnecessary for the current scope.

## Implementation Details
- Add five routes under `/reports/customers/...` for detail, region, responsibility, pricing, and tools inventory.
- Use the shared reports blueprint and the existing Flask app shell.
- Query customer relationships directly from the current models and render simple HTML tables and grouped sections.
- Keep the implementation server-side so the output remains deterministic and easy to test.

## Validation
- Added unit tests that exercise all five routes and assert the expected customer, market, pricing, and tool data appears in the rendered HTML.
- Ran the full pytest suite successfully.

## Consequences
- The reports are simple to extend and easy to inspect in a browser.
- No new runtime dependency is required.
- Future report variants can reuse the same data-access pattern.

## Monitoring & Rollback
- **Review date**: 2026-05-01
- **Success metric**: the routes continue to return the expected HTML for representative customer data.
- **Rollback strategy**: remove the customer report routes if a different rendering approach is later adopted.

## References
- `prd.json` F-053
- `src/ith_webapp/reports.py`
- `src/ith_webapp/models/customer.py`
- `src/ith_webapp/models/customer_application.py`
- `src/ith_webapp/models/customer_tools.py`
- `tests/unit/test_customer_reports.py`
