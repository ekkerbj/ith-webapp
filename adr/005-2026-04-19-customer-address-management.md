# ADR 005: Customer Address Management

**Date:** 2026-04-19  
**Status:** Accepted  
**Authors/Owners:** Team  
**Drivers:** PRD F-005, customer address CRUD, SAP/Access mapping  
**Tags:** customer, address, CRUD, SQLAlchemy, SAP, Access

## Decision
Implement a `CustomerAddress` model and table to support multiple addresses per customer, with address type as a foreign key, and full CRUD as a sub-resource of Customer.

## Context
- Requirement to support multiple addresses per customer (billing, shipping, etc.)
- Must map to Access customer address forms and dbo_CRD1 SAP address data
- Integrate with existing Customer CRUD (F-003)

## Alternatives Considered
- Embedding address fields in Customer table (rejected: does not support multiple addresses)
- Using a generic key-value store (rejected: lacks structure, poor query performance)
- Separate address table with FK to customer (chosen: normalized, scalable, aligns with SAP/Access)

## Implementation Details
- SQLAlchemy model `CustomerAddress` with fields: address_id (PK), customer_id (FK), address_type, street, city, state, zip_code, country
- Table: `customer_address`
- CRUD operations as sub-resource of Customer
- Unit test verifies persistence and retrieval

## Validation
- Unit test: `test_customer_address_can_be_persisted_and_retrieved` passes
- Table created and mapped in SQLAlchemy
- Manual DB inspection confirms structure

## Consequences
+ Supports multiple addresses per customer
+ Aligns with SAP/Access data model
+ Enables future address types/extensions
- Slightly more complex queries for address retrieval

## Monitoring & Rollback
- Review: 2026-06-01
- Success metrics: CRUD operations in production, no data integrity issues
- Rollback: Drop `customer_address` table, remove model and routes

## References
- PRD F-005
- SAP dbo_CRD1
- Access customer address forms
- tests/unit/test_customer_address_model.py
