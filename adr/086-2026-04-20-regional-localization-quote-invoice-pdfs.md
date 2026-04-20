# ADR 086: Regional Localization for Quote and Invoice PDFs

## Metadata
- Date: 2026-04-20
- Status: Accepted
- Authors: The AI
- Drivers: F-086 backlog item, Brazil/Mexico regional variants, deterministic PDF output, minimal dependency footprint
- Tags: reports, localization, pdf, quotes, invoices

## Decision
Implement region-aware formatting in the quote and invoice PDF builders so Brazil and Mexico variants render localized currency strings while keeping the existing in-repo PDF writer.

## Context
F-086 requires regional variants for legacy quote and invoice documents. The application already had region parameters on the relevant report routes, but monetary values were still rendered with a single non-regional format. The reporting stack is intentionally small and deterministic, so adding a locale library would increase surface area for a narrow formatting requirement.

## Alternatives Considered

### Add a locale package and rely on system locales
- **Pros**: broader formatting support.
- **Cons**: runtime dependency, environment-specific behavior, and extra deployment risk.
- **Rejected**: the required formatting can be expressed deterministically in code.

### Leave amounts in a single generic format
- **Pros**: no code change.
- **Cons**: does not satisfy the regional variant requirement and keeps the output closer to only one market.
- **Rejected**: the backlog explicitly calls for localized currency output.

## Implementation Details
- Extended the shared money formatter in `src/ith_webapp/reports.py` to accept an optional region code.
- Brazil (`BR`) amounts render as `R$ 1.234,56`.
- Mexico (`MX`) amounts render as `MX$ 1,234.56`.
- The service multi-quote and service invoice builders pass their region parameter into the formatter for totals and line-item prices/costs.
- Existing non-regional reports keep their current format.

## Validation
- Added unit tests that assert Brazil and Mexico invoice PDFs contain the expected localized currency strings.
- Ran `pytest -q` successfully.

## Consequences
- Quote and invoice PDFs now reflect the selected regional variant more clearly.
- Formatting remains deterministic and testable without a locale dependency.
- Additional regional rules will still need explicit code paths if future backlog items expand beyond BR and MX.

## Monitoring & Rollback
- Review when new regional markets or compliance rules are added.
- Success metric: regional PDFs continue to show the expected currency format and route output remains valid PDF bytes.
- Rollback strategy: revert the formatter change and region-specific call sites if a different localization approach is adopted.

## References
- `prd.json` F-086
- `src/ith_webapp/reports.py`
- `tests/unit/test_service_invoice_report.py`
- `adr/045-2026-04-19-service-multi-quote-pdf-report.md`
- `adr/046-2026-04-19-basic-quote-pdf-report.md`
