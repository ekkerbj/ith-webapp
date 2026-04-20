# ADR 087: Customer-Specific Report Variants

## Metadata
- Date: 2026-04-20
- Status: Accepted
- Authors: The AI
- Drivers: F-087 backlog item, legacy customer-specific report behavior, deterministic PDF output, minimal routing changes
- Tags: reports, pdf, customers, variants

## Decision
Implement customer-specific report variants by deriving the report title from the customer name for known legacy cases.

## Context
The backlog calls for customer-specific formatting on a small number of legacy reports, including an Alstom multi-quote and a Mortenson parts-picture variant. The reporting system already builds deterministic PDFs in-process, so the safest change is to branch on customer identity inside the report builder rather than introduce a new routing layer or configuration store.

## Alternatives Considered
- **Separate routes for every customer variant**: rejected because it would multiply endpoints and duplicate the same report logic.
- **Database-driven variant configuration**: rejected because the backlog only needs a few stable legacy cases and the extra schema would add maintenance overhead.
- **Leave all customer reports generic**: rejected because it would not model the known Access-specific variants.

## Implementation Details
- Added a small helper in `src/ith_webapp/reports.py` that maps customer names containing `Alstom` and `Mortenson` to legacy variant titles.
- The service multi-quote PDF now renders `Alstom Multi Quote` for Alstom customers.
- The customer-specific parts list PDF now renders `Mortenson Part Pics` for Mortenson customers.
- Other customers continue to use the existing generic report titles.

## Validation
- Added unit tests covering the Alstom and Mortenson variants.
- Ran the full test suite successfully (`pytest -q`).

## Consequences
- Legacy customer-specific report names are visible in deterministic PDFs without adding new dependencies.
- The implementation remains small and easy to extend if more customer-specific variants are discovered.
- Customer matching is string-based, so future edge cases may require additional normalization rules.

## Monitoring & Rollback
- Review when additional legacy customer variants appear.
- Success metric: the expected customer-specific titles continue to appear in generated PDFs.
- Rollback strategy: remove the helper and revert to the generic report titles if the mapping proves too narrow.

## References
- `prd.json` F-087
- `src/ith_webapp/reports.py`
- `tests/unit/test_customer_specific_report_variants.py`
- `adr/045-2026-04-19-service-multi-quote-pdf-report.md`
- `adr/056-2026-04-19-parts-catalog-report.md`
