# ADR 090: DN Import List HTML Report

## Metadata
- Date: 2026-04-20
- Status: Accepted
- Authors: The AI
- Drivers: F-090 backlog item, deterministic HTML output, reuse of existing sales and part tables
- Tags: reports, html, parts_sold, import

## Decision
Implement the legacy DN Import List as a server-rendered HTML report on the existing reports blueprint, sourced from `PartsSold` rows joined to `Part`.

## Context
F-090 replaces the legacy Access DNImport report. The codebase already stores sold delivery-note-like rows in `parts_sold`, and each row can be enriched with part metadata from `part`. A lightweight HTML report is sufficient for reviewing the imported rows without introducing a new persistence model or export pipeline.

## Alternatives Considered

### Add a dedicated import table
- **Pros**: could store staged import snapshots.
- **Cons**: duplicates the source of truth and expands schema surface.
- **Rejected**: existing `parts_sold` rows already represent the needed data.

### Generate only a PDF version
- **Pros**: better for printing.
- **Cons**: less convenient for validating import rows interactively.
- **Rejected**: the backlog explicitly calls for HTML.

### Fold the report into parts sold history
- **Pros**: reuses the same source records.
- **Cons**: mixes two distinct user-facing report intents.
- **Rejected**: the import list needs its own route and title.

## Implementation Details
- Added `/reports/dn-import-list` with `/reports/dn-import` as an alias.
- The route queries `PartsSold` joined to `Part`, ordered by sold date and row ID.
- The template renders sold date, part number, description, quantity, and an empty-state row.

## Validation
- Added unit coverage for the HTML report route with representative `PartsSold` and `Part` records.
- Ran the full pytest suite successfully.

## Consequences
- The DN Import List is now viewable in-browser using existing data.
- The report stays aligned with the current schema instead of introducing staging tables.
- Future Access-report ports can reuse the same reports-blueprint pattern.

## Monitoring & Rollback
- Review after the next import-oriented backlog item lands.
- Success metric: the report continues to render the expected sold rows without regressions.
- Rollback strategy: remove the route, helper, template, tests, and this ADR if a different import workflow is adopted.

## References
- `prd.json` F-090
- `src/ith_webapp/reports.py`
- `tests/unit/test_dn_import_list_report.py`
- `src/ith_webapp/models/parts_sold.py`
- `src/ith_webapp/models/part.py`
