# ADR 056: Parts Catalog Report as HTML and PDF

## Metadata
- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-056 backlog item, deterministic report output, reuse of existing parts master and BOM models
- **Tags**: reports, parts, pdf, html, catalog

## Decision
Implement the parts catalog surface on the existing reports blueprint as both server-rendered HTML and generated PDF output.

## Context
F-056 replaces legacy Access catalog/item reports. The codebase already has a parts master model, BOM tables, and customer-side part references through consignment inventory. The report needs to show part identity, BOM usage, and customer cross-references without introducing a new reporting subsystem.

## Alternatives Considered

### Add a separate catalog service
- **Pros**: isolates report logic from the main app.
- **Cons**: more infrastructure and a wider deployment surface.
- **Rejected**: unnecessary for a deterministic, database-backed report.

### Generate only PDF
- **Pros**: matches printable legacy reports.
- **Cons**: harder to inspect interactively and less reusable in the UI.
- **Rejected**: the backlog explicitly calls for PDF/HTML.

### Add new tables for images and cross-reference metadata first
- **Pros**: could store richer catalog data.
- **Cons**: would expand scope beyond the report requirement.
- **Rejected**: the existing data model is sufficient for the initial report.

## Implementation Details
- Added `/reports/parts/<part_id>` for HTML output and `/reports/parts/<part_id>/pdf` for PDF output.
- Added `build_parts_catalog_pdf()` to reuse the same catalog context for export.
- The report reads from `Part`, `PartsList`, `PartsSub`, and `ConsignmentList`.
- The HTML and PDF surfaces include item identity, an image section with a fallback message, BOM usage, and customer cross-references.

## Validation
- Added unit coverage for the PDF builder and HTML route.
- Ran the full pytest suite successfully.

## Consequences
- The catalog report is usable both in-browser and as a printable export.
- The report stays aligned with the current schema instead of requiring new catalog tables.
- Future image storage or richer cross-reference data can extend the same report context.

## Monitoring & Rollback
- **Review date**: 2026-05-01
- **Success metric**: the report continues to render the expected catalog sections for representative parts data.
- **Rollback strategy**: remove the report routes, helper functions, tests, and this ADR if a different catalog approach is adopted.

## References
- `prd.json` F-056
- `src/ith_webapp/reports.py`
- `tests/unit/test_parts_catalog_report.py`
- `src/ith_webapp/models/part.py`
- `src/ith_webapp/models/parts_list.py`
- `src/ith_webapp/models/consignment_list.py`
