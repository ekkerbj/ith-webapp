# ADR 012: Check In Sub Model and Workflow

**Date:** 2026-04-19  
**Status:** Accepted  
**Authors:** The AI, project team  
**Drivers:** F-013 (Check In Sub Items and Workflow), F-012 (Check In Header), F-011 (Customer Tools)  
**Tags:** model, workflow, check-in, sub-resource, SQLAlchemy, alembic

## Decision
Implement the CheckInSub model and table to represent individual tools checked in as line items, with boolean workflow flags (inspected, quoted, approved, closed). Establish a relationship to CheckIn. CRUD operations are provided as sub-resources of CheckIn. Workflow progression logic is enforced at the application layer.

## Context
- F-013 requires tracking each tool checked in as a sub-item of a CheckIn, with workflow state flags.
- No prior check_in_sub table or model existed.
- SQLAlchemy and Alembic are used for ORM and migrations.
- F-012 (Check In Header) and F-011 (Customer Tools) are dependencies.

## Alternatives Considered
- **Single status field:** Not flexible for multi-stage workflow.
- **Separate tables for each workflow state:** Overly complex, not scalable.
- **Boolean flags on a single model:** Simple, clear, supports linear workflow.

## Implementation Details
- Add CheckInSub model (check_in_sub table) with FK to check_in and tool_id.
- Boolean fields: inspected, quoted, approved, closed.
- Relationship from CheckIn to CheckInSub (one-to-many).
- Alembic migration to create the table.
- Unit test for persistence and workflow flags.

## Validation
- Unit test: CheckInSub can be persisted and retrieved with correct workflow flags.
- Alembic migration applies cleanly.
- All tests pass after implementation.

## Consequences
+ Enables tracking of individual tool check-in workflow.
+ Foundation for future workflow automation.
+ Minimal performance impact; standard SQLAlchemy pattern.

## Monitoring & Rollback
- Review after first production use.
- Rollback: Drop check_in_sub table if needed.

## References
- F-013 in prd.json
- SQLAlchemy documentation: One-to-many relationships
- Alembic migration scripts
