# ADR 052: Service Measurements and Test Reports PDF

## Metadata
- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-052 PDF output, service measurement form coverage, deterministic server rendering, minimal dependency footprint
- **Tags**: reports, PDF, service measurements, Flask

## Decision
Implement the service measurements and test reports as a Flask blueprint route backed by the in-repo PDF writer. The report renders six tool-specific measurement forms and six matching test report pages from the existing service and service measurement tables.

## Context
F-052 requires PDF outputs for the legacy Access measurement forms and test reports. The application already stores the service order and a single service measurement record per service, so the report can be generated deterministically without adding a third-party PDF renderer.

## Alternatives Considered

### Add a third-party PDF renderer
- **Pros**: richer layout support and less low-level PDF code.
- **Cons**: new dependency, packaging risk, and more maintenance surface.
- **Rejected**: unnecessary for the current report scope.

### Generate HTML and print it as PDF in the browser
- **Pros**: simpler server code.
- **Cons**: inconsistent output and weaker testability.
- **Rejected**: the report should stay server-rendered and deterministic.

## Implementation Details
- Add `build_service_measurements_pdf(session, service_id)` to `src/ith_webapp/reports.py`.
- Query `Service` and `ServiceMeasurements` for the requested service order.
- Render 12 pages: measurement form and test report pages for BTC, Gauge, Hose, Nut Runner, Pump, and Torque Wrench.
- Include customer, card code, service ID, and the tool-specific measurement value on each page.
- Expose `/reports/service-measurements/<service_id>` as a PDF response.

## Validation
- Added unit tests that create a service with measurements and assert the generated PDF contains the expected tool report titles and measurement values.
- Added a route test that verifies the report endpoint returns PDF bytes.

## Consequences
- The report is deterministic and easy to test.
- No new runtime dependency is required.
- Future service-document reports can reuse the same writer and service lookup pattern.

## Monitoring & Rollback
- **Review date**: 2026-05-01
- **Success metric**: the report route continues to return valid PDF bytes for service measurement records.
- **Rollback strategy**: remove the report function and route if a different rendering approach is adopted later.

## References
- `prd.json` F-052
- `src/ith_webapp/reports.py`
- `src/ith_webapp/models/service.py`
- `src/ith_webapp/models/service_measurements.py`
- `tests/unit/test_service_measurements_report.py`
