# ADR 048: Check In PDF Report

## Metadata
- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-048 PDF output, tool receipt layout, deterministic server rendering, minimal dependency footprint
- **Tags**: reports, PDF, check-in, Flask

## Decision
Implement the Check In report as a Flask blueprint route backed by the existing in-repo PDF writer. The report renders a tool receipt record with customer metadata and a list of received tools.

## Context
The backlog requires a Check In PDF that mirrors the legacy Access output. The application already uses a small deterministic PDF writer for report-style documents, and the check-in layout is simple enough to avoid a third-party rendering dependency.

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
- Add `build_check_in_pdf(session, check_in_id)` to `src/ith_webapp/reports.py`.
- Query `CheckIn` and related `CheckInSub` rows to render the receipt.
- Render a tool receipt record section plus a received-tools list.
- Expose `/reports/check-in/<check_in_id>` as a PDF response.
- Reuse the existing PDF pagination and writer helpers.

## Validation
- Added unit tests that create a check-in with tool rows and assert the generated PDF contains the expected report sections and route response headers.
- Ran the full pytest suite successfully.

## Consequences
- The report is deterministic and easy to test.
- No new runtime dependency is required.
- Future receipt-style reports can reuse the same writer.

## Monitoring & Rollback
- **Review date**: 2026-05-01
- **Success metric**: the report route continues to return valid PDF bytes for check-ins.
- **Rollback strategy**: remove the report function and route if a different rendering approach is adopted later.

## References
- `prd.json` F-048
- `src/ith_webapp/reports.py`
- `src/ith_webapp/models/check_in.py`
- `tests/unit/test_check_in_report.py`
