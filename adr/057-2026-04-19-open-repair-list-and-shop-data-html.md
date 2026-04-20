# ADR 057: Open Repair List and Shop Data as HTML Reports

## Metadata
- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-057 backlog item, deterministic HTML output, reuse of the existing reports blueprint, no new persistence model required
- **Tags**: reports, html, check-in, service, shop-data

## Decision
Implement the legacy Open Repair List and ITH Shop Data reports as server-rendered HTML pages on the existing reports blueprint.

## Context
F-057 replaces Access reports that are driven by existing check-in and service records. The application already has a reports blueprint, deterministic server-side rendering patterns, and enough relational data to produce the reports without adding new tables or an export pipeline.

## Alternatives Considered

### Generate PDF versions instead of HTML
- **Pros**: matches other printable report surfaces.
- **Cons**: unnecessary for tabular operational reports that are easier to inspect in a browser.
- **Rejected**: the backlog explicitly calls for HTML.

### Combine both reports into one mixed-purpose page
- **Pros**: fewer routes.
- **Cons**: weaker separation between repair queue data and shop throughput data.
- **Rejected**: the legacy reports are distinct and should remain individually addressable.

### Add new reporting tables first
- **Pros**: could store curated report snapshots.
- **Cons**: expands scope and duplicates existing source-of-truth records.
- **Rejected**: the current schema already supports the report requirements.

## Implementation Details
- Added `/reports/check-in/open-repair-list` for the open repair queue.
- Added `/reports/shop-data` for technician workload and throughput summary data.
- The open repair list filters to unclosed `CheckInSub` rows and renders customer, receipt, and tool details.
- The shop data report groups `ServiceTime` rows by technician and summarizes statuses, service count, total hours, and total labor.
- Both routes use local helper functions and `render_template_string` for deterministic output.

## Validation
- Added unit coverage for both HTML routes with representative check-in and service records.
- Ran the full pytest suite successfully.

## Consequences
- The reports are browser-friendly and easy to validate.
- The implementation stays aligned with the existing schema instead of introducing new models.
- Future report expansions can reuse the same route-and-template pattern.

## Monitoring & Rollback
- **Review date**: 2026-05-01
- **Success metric**: the two report pages continue to render the expected rows for representative operational data.
- **Rollback strategy**: remove the routes, helper functions, tests, and this ADR if the reporting approach changes.

## References
- `prd.json` F-057
- `src/ith_webapp/reports.py`
- `tests/unit/test_open_repair_list_and_shop_data_report.py`
