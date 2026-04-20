# ADR 073: Customer-Specific Pricing Display

## Metadata
- Date: 2026-04-20
- Status: Accepted
- Authors: The AI
- Drivers: F-073 backlog item, SAP pricing comparison needs, deterministic HTML reporting, reuse of the existing reports blueprint
- Tags: reports, sap, pricing, customers, html

## Decision
Implement the customer pricing report as a server-rendered HTML view on the reports blueprint that compares customer-specific SAP prices (OSPP) with standard price-list prices (ITM1) and flags basic price-integrity status.

## Context
The backlog requires a report that shows customer-specific pricing alongside standard pricing. The project already has a customer-report HTML surface, SAP repository protocols for price lookup, and a local part catalog that can provide item codes for comparison. The report must stay deterministic and testable without requiring a live SAP connection.

## Alternatives Considered
- **PDF output**: rejected because the report is tabular and easier to scan in HTML.
- **Direct SAP queries in the view**: rejected because it would bypass the repository abstraction and reduce testability.
- **A separate reporting subsystem**: rejected because the existing Flask reports blueprint already fits the scope.

## Implementation Details
- Extended `/reports/customers/pricing` to render a comparison table.
- When SAP repositories are configured, the report compares each customer against local parts, resolves customer-specific and standard prices through repository calls, and labels rows with a simple integrity status.
- When SAP repositories are not configured, the route falls back to the existing customer summary display so the older customer pricing view remains usable.
- The HTML labels the two SAP price sources as OSPP and ITM1 to match the legacy report naming.

## Validation
- Added a unit test that exercises customer-specific and standard pricing output with fake SAP repositories.
- Confirmed the existing customer pricing/report inventory test still passes.
- Ran `pytest -q` successfully.

## Consequences
- Pricing comparisons are visible in a browser without adding a new dependency.
- The report stays compatible with older customer-only usage.
- The route now depends on SAP repository configuration for the comparison mode.

## Monitoring & Rollback
- Review after the first real SAP adapter is wired to confirm the part catalog and repository methods still match the available item and price data.
- Roll back by restoring the prior customer-only pricing template if the comparison view needs a different shape.

## References
- `prd.json` F-073
- `src/ith_webapp/reports.py`
- `src/ith_webapp/repositories/sap_repository.py`
- `tests/unit/test_customer_reports.py`
- `adr/038-2026-04-19-sap-repository-interface-abstraction.md`
- `adr/039-2026-04-19-sap-pricing-waterfall.md`
