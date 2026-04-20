# ADR 094: Field Service Hours Graph Report

## Metadata
- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-094 backlog item, field-service hours visibility, deterministic server-side PDF output, no new charting dependency
- **Tags**: reports, PDF, field-service, hours, graph

## Decision
Implement the Field Service Hours Graph as a PDF report route backed by the existing in-repo PDF writer. The report aggregates service-time hours by date for the customer linked to the selected field service record and renders a simple text-based bar graph.

## Context
F-094 requires a Field Service Hours Graph report to mirror the legacy Access output. The application already stores field service records, services, and service-time entries, and the report layer already produces deterministic PDFs without external rendering libraries. A text-based graph keeps the implementation testable and avoids introducing a charting dependency for a single report.

## Alternatives Considered

### Add a charting library and render SVG/bitmap output
- **Pros**: visual graph output.
- **Cons**: new runtime dependency and more packaging complexity.
- **Rejected**: the report scope is narrow and the existing PDF writer is sufficient.

### Reuse the field service summary report
- **Pros**: no new report code.
- **Cons**: no graph-style output and no date-level aggregation.
- **Rejected**: the report needs its own presentation.

## Implementation Details
- Added `build_field_service_hours_graph_pdf(session, field_service_id)` to `src/ith_webapp/reports.py`.
- Added helpers that aggregate `ServiceTime.hours` by `date` for the customer linked to the selected `FieldService`.
- Rendered each date as a bar line in the PDF using repeated ASCII `#` characters and a formatted hour total.
- Exposed `/reports/field-service-hours-graph/<field_service_id>` as a PDF response.

## Validation
- Added unit coverage for the PDF builder and the route.
- The full pytest suite passes after the change.

## Consequences
- The report remains deterministic and easy to test.
- No new charting dependency is introduced.
- The graph is text-based rather than a rendered plot, which preserves simplicity at the cost of visual richness.

## Monitoring & Rollback
- **Review date**: 2026-05-01
- **Success metric**: the graph route continues to return valid PDF bytes and reflects the customer's aggregated service hours by date.
- **Rollback strategy**: remove the graph helpers and route, then revert this ADR and the backlog status update.

## References
- `prd.json` F-094
- `src/ith_webapp/reports.py`
- `tests/unit/test_field_service_report.py`
- `src/ith_webapp/models/field_service.py`
- `src/ith_webapp/models/service_time.py`
