# ADR 093: Service Packet PDF Report

## Metadata
- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-093 PDF output, bundled service documentation, deterministic server rendering, minimal dependency footprint
- **Tags**: reports, PDF, service, Flask

## Decision
Implement the Service Packet report as a Flask blueprint route backed by the in-repo PDF writer. The report renders a packet cover page, the Service Multi Quote pages, any available Service Measurements pages, and optional ITH Test Gauge certificate pages into one PDF.

## Context
F-093 requires a single service packet document that combines several legacy Access outputs into one multi-page PDF. The codebase already has deterministic PDF helpers for service quotes, measurements, and gauge certificates, so the packet can be assembled without introducing a third-party PDF renderer.

## Alternatives Considered

### Add a third-party PDF merger
- **Pros**: explicit PDF concatenation support.
- **Cons**: new dependency and extra packaging risk.
- **Rejected**: the existing writer and page helpers are sufficient for the current scope.

### Generate HTML and print it in the browser
- **Pros**: simpler server code.
- **Cons**: inconsistent output and weaker testability.
- **Rejected**: the packet needs deterministic server-side PDF output.

## Implementation Details
- Add `build_service_packet_pdf(session, service_id, region=None, variant=None, ith_test_gauge_id=None)` to `src/ith_webapp/reports.py`.
- Reuse internal page helpers for Service Multi Quote, Service Measurements, and ITH Test Gauge certificates.
- Add a packet cover page so the combined document remains identifiable.
- Expose `/reports/service-packet/<service_id>` as a PDF response.
- Accept `region`, `variant`, and `gauge_id` query parameters for the optional bundled sections.

## Validation
- Added unit tests that create service, measurement, and gauge data and assert the packet PDF contains the expected report titles.
- Added a route test that verifies the packet endpoint returns PDF bytes.
- Ran the full pytest suite successfully.

## Consequences
- The packet remains deterministic and easy to test.
- The implementation avoids a new runtime dependency.
- Optional gauge certificate bundling keeps the report flexible without adding a new data relation.

## Monitoring & Rollback
- **Review date**: 2026-05-01
- **Success metric**: the packet route continues to return valid PDF bytes and includes the expected bundled sections.
- **Rollback strategy**: remove the packet builder and route if the legacy output needs a different assembly approach later.

## References
- `prd.json` F-093
- `src/ith_webapp/reports.py`
- `src/ith_webapp/models/service.py`
- `src/ith_webapp/models/service_measurements.py`
- `src/ith_webapp/models/ith_test_gauge.py`
- `tests/unit/test_service_packet_report.py`
