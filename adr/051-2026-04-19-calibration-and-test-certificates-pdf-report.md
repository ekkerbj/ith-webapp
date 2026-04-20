# ADR 051: Calibration and Test Certificates PDF Report

## Metadata
- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-051 PDF output, gauge certification layout, deterministic server rendering, minimal dependency footprint
- **Tags**: reports, PDF, ITH test gauge, certification, Flask

## Decision
Implement the ITH Test Gauge certificate report as a Flask blueprint route backed by the in-repo PDF writer. The report renders gauge calibration, force test, and torque test certificate pages from the existing gauge and gauge type tables.

## Context
F-051 requires formal certification documents for ITH test gauges. The application already stores the gauge name, serial number, type, and due dates in dedicated SQLAlchemy models, so the report can be generated deterministically without adding a third-party PDF renderer.

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
- Add `build_ith_test_gauge_certificates_pdf(session, ith_test_gauge_id, variant=None)` to `src/ith_webapp/reports.py`.
- Query `ITHTestGauge` and render three pages: Gauge Calibration Certificate, Force Test Certificate, and Torque Test Certificate.
- Include gauge name, serial number, type, calibration due date, certification due date, and an ISO 17025 variant label when requested.
- Expose `/reports/ith-test-gauge-certificates/<ith_test_gauge_id>` as a PDF response.
- Reuse the existing PDF pagination and writer helpers.

## Validation
- Added unit tests that create a gauge and assert the generated PDF contains the expected certificate titles and gauge data.
- Added a route test that verifies the report endpoint returns PDF bytes.
- Ran the full pytest suite successfully.

## Consequences
- The report is deterministic and easy to test.
- No new runtime dependency is required.
- Future gauge certification outputs can reuse the same writer and data source.

## Monitoring & Rollback
- **Review date**: 2026-05-01
- **Success metric**: the report route continues to return valid PDF bytes for ITH test gauges.
- **Rollback strategy**: remove the report function and route if a different rendering approach is adopted later.

## References
- `prd.json` F-051
- `src/ith_webapp/reports.py`
- `src/ith_webapp/models/ith_test_gauge.py`
- `src/ith_webapp/models/ith_test_gauge_type.py`
- `tests/unit/test_ith_test_gauge_report.py`
