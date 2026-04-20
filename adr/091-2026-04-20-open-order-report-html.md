# ADR 091: Open Order Report HTML

## Metadata
- Date: 2026-04-20
- Status: Accepted
- Authors: The AI
- Drivers: F-091 backlog item, customer-specific SAP order visibility, deterministic HTML output
- Tags: reports, html, sap, orders, customers

## Decision
Implement the Open Order Report as server-rendered HTML on the existing reports blueprint. The report resolves a customer from the local database and renders that customer's open SAP orders through a repository object exposed as `SAP_ORDER_REPOSITORY`.

## Context
F-091 replaces the legacy customer-specific open order report. The application already stores customer identity and SAP card codes locally, but it does not maintain a separate open-order table. The reporting surface needs to stay deterministic and testable without binding the app to a concrete SAP connector.

## Alternatives Considered

### Add a new open-order persistence model
- **Pros**: could cache SAP order rows locally.
- **Cons**: duplicates SAP data and adds synchronization concerns.
- **Rejected**: the report only needs read-only visibility.

### Query SAP directly inside the route
- **Pros**: minimal surface area.
- **Cons**: couples the view to a transport-specific implementation.
- **Rejected**: the reports blueprint should depend on a narrow repository seam.

### Generate only a PDF
- **Pros**: printable output.
- **Cons**: harder to review interactively.
- **Rejected**: the backlog item explicitly calls for HTML.

## Implementation Details
- Added `/reports/open-order/<customer_id>` with `/reports/open-order-report/<customer_id>` as an alias.
- The route loads the customer by ID, reads the customer `card_code`, and calls `SAP_ORDER_REPOSITORY.list_open_orders(card_code)`.
- The template renders customer identity plus a simple table of doc entry, order number, and total.
- Empty order sets render a placeholder row rather than failing.

## Validation
- Added unit coverage for the report route using an in-memory SQLite customer row and a fake open-order repository.
- Ran the full pytest suite successfully.

## Consequences
- Customer-specific open orders are now reviewable in-browser.
- The report stays decoupled from any specific SAP transport.
- Future SAP adapters must supply an open-order listing method for this report surface.

## Monitoring & Rollback
- Review after the next SAP reporting backlog item lands.
- Success metric: the report continues to render representative open-order rows without regression.
- Rollback strategy: remove the route, helper, template, tests, and this ADR if a different open-order workflow is adopted.

## References
- `prd.json` F-091
- `src/ith_webapp/reports.py`
- `tests/unit/test_open_order_report.py`
- `src/ith_webapp/models/customer.py`
- `src/ith_webapp/repositories/sap_repository.py`
