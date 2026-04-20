# ADR 039: SAP Pricing Waterfall Service

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI
- Drivers: F-039 backlog item, pricing precedence from legacy SAP logic, testable pricing rules for future quote and inventory work
- Tags: sap, pricing, service, waterfall, pricing rules

## Decision
Implement SAP pricing as a small service function that resolves price in this order: BP-specific price, then price-list price, then a purchase-price floor, with a special lower floor for customer `C007134`.

## Context
The legacy Access behavior described in F-039 depends on SAP-linked pricing data and a fixed precedence chain. The codebase already exposes SAP data through small repository protocols, so pricing logic can stay isolated from the eventual connector implementation.

## Alternatives Considered
- Inline pricing logic at each call site: rejected because it would duplicate the waterfall and make future rule changes risky.
- A larger pricing engine class: rejected because the current rule set is small and a single pure service function is sufficient.
- Hardcoding prices in tests or views: rejected because it would bypass the repository abstraction and hide the real precedence rules.

## Implementation Details
- Added `src/ith_webapp/services/sap_pricing.py` with `set_price(...)`.
- The function first returns the BP-specific price when present.
- If no BP price exists, it reads the customer price list and item purchase price.
- The floor is `1.2x` purchase price for normal customers and `1.1x` for `C007134`.
- The returned value is the greater of the price-list price and the applicable floor.

## Validation
- `pytest -q tests/unit/test_sap_pricing.py`
- `pytest -q`

## Consequences
- Pricing logic is centralized and testable.
- The Brazil-specific exception is explicit instead of implicit in scattered business logic.
- Future SAP pricing changes will need updates in one place and in a focused test file.

## Monitoring & Rollback
- Review when additional SAP pricing rules appear, especially if taxes, discounts, or currencies need to be incorporated.
- Roll back by removing the service module, its tests, and this ADR if the legacy behavior is replaced by a different pricing component.

## References
- F-039 in `prd.json`
- `src/ith_webapp/repositories/sap_repository.py`
- `src/ith_webapp/services/sap_pricing.py`
- `tests/unit/test_sap_pricing.py`
