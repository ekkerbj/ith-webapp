# ADR 038: SAP Repository Interface Abstraction

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI
- Drivers: F-038 backlog item, future SAP connector swapability, testable boundaries for pricing and inventory work
- Tags: sap, repositories, protocol, abstraction, pricing, inventory

## Decision
Define runtime-checkable repository protocols and small record dataclasses in `src/ith_webapp/repositories/sap_repository.py` for SAP-linked reads.

## Context
Later backlog items need access to SAP customer, item, price, invoice, order, and warehouse data, but the connector itself is not ready. A narrow abstraction now keeps the rest of the codebase independent from the eventual transport choice while still giving future work a stable contract.

## Alternatives Considered
- Concrete SAP client classes now: rejected because the connector implementation is deferred and would force premature transport decisions.
- Abstract base classes with `NotImplementedError`: rejected because structural typing is enough here and keeps adapters lightweight.
- Passing raw dictionaries around: rejected because it weakens intent and makes later call sites harder to reason about.

## Implementation Details
- Added `SapCustomerRepository`, `SapItemRepository`, `SapPriceRepository`, `SapInvoiceRepository`, `SapOrderRepository`, and `SapWarehouseRepository` as `Protocol`s.
- Marked each protocol `@runtime_checkable` so simple test doubles can satisfy the contract without inheritance.
- Added small frozen dataclasses for the common SAP read models used by the protocols.
- Kept the module self-contained so later ODBC, REST, or mock adapters can implement the same API without changing call sites.

## Validation
- `pytest -q tests/unit/test_sap_repository_interfaces.py`
- `pytest -q`

## Consequences
- Future SAP access can be swapped behind a stable contract.
- Tests can use lightweight fakes without a live SAP dependency.
- The codebase now has an explicit place for SAP read models, which makes later pricing and inventory work easier to wire.

## Monitoring & Rollback
- Review when the first real SAP adapter is implemented to confirm the protocol surface still matches the connector needs.
- Roll back by removing `src/ith_webapp/repositories/sap_repository.py`, the related test, and this ADR if a different integration boundary is chosen.

## References
- F-038 in `prd.json`
- `src/ith_webapp/repositories/sap_repository.py`
- `tests/unit/test_sap_repository_interfaces.py`
