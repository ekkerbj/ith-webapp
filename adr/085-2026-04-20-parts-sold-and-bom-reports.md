# ADR 085: Parts Sold and BOM Reports as HTML and PDF

## Metadata
- Date: 2026-04-20
- Status: Accepted
- Authors: The AI
- Drivers: F-085 backlog item, printable report output, reuse of existing parts/customer/BOM models
- Tags: reports, parts, pdf, html, bom

## Decision
Implement the parts sold history, assembly parts list, and customer-specific parts list on the existing reports blueprint with paired HTML and PDF surfaces.

## Context
F-085 replaces legacy Access parts list/BOM reports. The codebase already has the required data sources: `PartsSold` for sales history, `PartsList`/`PartsSub` for assembly BOMs, and `Customer`/`ConsignmentList` for customer-specific parts lists. The report family needed deterministic output without introducing a new reporting subsystem.

## Alternatives Considered

### Add a separate parts-report service
- **Pros**: isolates report logic from the main app.
- **Cons**: additional deployment surface and extra integration work.
- **Rejected**: unnecessary for deterministic database-backed reports.

### Generate only PDFs
- **Pros**: aligns with printable legacy reports.
- **Cons**: harder to inspect in-browser and less useful for interactive review.
- **Rejected**: the backlog explicitly calls for PDF/HTML output.

### Reuse only the existing `/parts` subresource views
- **Pros**: fewer routes.
- **Cons**: mixes end-user subresources with report exports and leaves PDF output incomplete.
- **Rejected**: the report outputs need a dedicated reporting namespace.

## Implementation Details
- Added `/reports/parts-sold/<part_id>` and `/reports/parts-sold/<part_id>/pdf`.
- Added `/reports/parts-list/<parts_list_id>` and `/reports/parts-list/<parts_list_id>/pdf`.
- Added `/reports/customer-parts-list/<customer_id>` and `/reports/customer-parts-list/<customer_id>/pdf`.
- Each report uses a shared context helper plus a PDF line builder to keep HTML and PDF content aligned.
- The reports read directly from `Part`, `PartsSold`, `PartsList`, `PartsSub`, `Customer`, and `ConsignmentList`.

## Validation
- Added unit coverage for each PDF builder and HTML route.
- Ran `pytest -q` successfully.

## Consequences
- Parts sales and BOM data can now be reviewed in-browser and exported for printing.
- The report family stays aligned with the existing schema instead of introducing extra tables.
- Future report variants can reuse the same context-and-line pattern.

## Monitoring & Rollback
- Review after the next parts-related backlog item lands.
- Success metric: the report surfaces continue to render representative parts data without regression.
- Rollback strategy: remove the routes, helpers, tests, and this ADR if a different parts reporting approach is adopted.

## References
- `prd.json` F-085
- `src/ith_webapp/reports.py`
- `tests/unit/test_parts_reports.py`
- `src/ith_webapp/models/parts_sold.py`
- `src/ith_webapp/models/parts_list.py`
- `src/ith_webapp/models/consignment_list.py`
