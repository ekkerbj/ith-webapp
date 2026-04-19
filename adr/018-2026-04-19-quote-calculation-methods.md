# ADR 018: Quote Calculation Methods for ServiceMeasurements

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI
- Drivers: F-020 (Quote Calculations), business logic normalization
- Tags: calculation, model, SQLAlchemy, quote, sum
- Supersedes: None
- Superseded By: None

## Decision
Add `item_sum(session)` and `labor_sum(session)` methods to the `ServiceMeasurements` model to encapsulate business logic for summing item and labor costs for a given service order, as required for quote calculations.

## Context
F-020 requires the system to calculate the total item and labor costs for a service order, replacing legacy Access logic (modItemLabor.txt). The new approach centralizes this logic in the model, using SQLAlchemy queries for maintainability and testability.

## Alternatives Considered
- Calculation in the view/controller: Rejected for violating separation of concerns and reusability.
- Calculation via raw SQL: Rejected for maintainability and ORM integration.
- Calculation in a service layer: Acceptable, but model method chosen for directness and testability.

## Implementation Details
- Methods `item_sum(session)` and `labor_sum(session)` added to `ServiceMeasurements`.
- Each method queries `ServiceSub` for the relevant `service_id` and `item_type` ('I' for item, 'L' for labor), summing the `cost` field.
- Unit test added in `test_service_measurements_calculations.py`.

## Validation
- Unit test verifies correct sum for both item and labor costs.
- All tests pass after implementation.

## Consequences
+ Centralizes quote calculation logic for maintainability
+ Enables future extension (e.g., discounts, taxes)
- Slight coupling between models

## Monitoring & Rollback
- Review after first production use for accuracy and performance
- Rollback by removing methods and reverting test if needed

## References
- F-020 in prd.json
- test_service_measurements_calculations.py
