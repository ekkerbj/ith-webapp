# ADR 007: Customer Communication Log Model

**Date:** 2026-04-19  
**Status:** Accepted  
**Authors:** The AI, project team  
**Drivers:** F-007 in prd.json  
**Tags:** model, customer, communication, SQLAlchemy, CRUD

## Decision
Implement a `CustomerCommunicationLog` SQLAlchemy model to track customer interactions, with a corresponding test and integration into the project models package.

## Context
The Access database and business requirements specify a need to track communication history per customer. This is mapped to a new `customer_communication_log` table, with a relationship to the `customer` table. The model must support CRUD operations and be testable in isolation.

## Alternatives Considered
- **No log model:** Rejected; does not meet requirements.
- **Flat text field on Customer:** Rejected; does not support multiple log entries or structured data.
- **Separate microservice:** Overkill for current scope.

## Implementation Details
- New file: `models/customer_communication_log.py` with SQLAlchemy model.
- Fields: log_id (PK), customer_id (FK), note (Text), created_at (DateTime, default UTC).
- Relationship: Many logs per customer.
- Registered in `models/__init__.py`.
- Unit test: `test_customer_communication_log_model.py` verifies creation and retrieval.

## Validation
- All tests pass (unit test for model, integration with customer).
- Manual DB inspection confirms table and relationships.

## Consequences
- Enables tracking of customer communications.
- Supports future CRUD UI and reporting.
- Minimal performance impact.

## Monitoring & Rollback
- Review after first production use.
- Rollback: Remove model and table if not needed.

## References
- prd.json F-007
- Access database schema
- SQLAlchemy documentation
