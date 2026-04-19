# ADR 017: ServiceFlag and ServiceFlagAssignment Models

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI
- Drivers: F-018 Service Flags requirement
- Tags: model, migration, service, flag
- Supersedes: None
- Superseded By: None

## Decision
Implement `ServiceFlag` and `ServiceFlagAssignment` SQLAlchemy models and migrations to support service order flagging.

## Context
F-018 in prd.json requires a flexible flag/alert system for service orders, mapping to Access rptService Flag reports. This enables tracking and assignment of arbitrary flags to service records.

## Alternatives Considered
- **Single flag field on Service**: Too rigid, does not support multiple or dynamic flags.
- **Separate flag table with M2M assignment**: Chosen for flexibility and normalization.

## Implementation Details
- `ServiceFlag` model: id, name, description.
- `ServiceFlagAssignment` model: id, service_id (FK), flag_id (FK).
- Alembic migration generated and applied.
- Unit tests created for both models.

## Validation
- All tests pass (unit and integration).
- Alembic migration applies cleanly.
- Models importable and instantiable.

## Consequences
- Enables dynamic flagging of service orders.
- Normalized schema supports future extensibility.
- No negative impacts identified.

## Monitoring & Rollback
- Review: 2026-05-01
- Success: Flags can be created, assigned, and queried in test and dev environments.
- Rollback: Revert migration and model files if issues arise.

## References
- prd.json F-018
- Access rptService Flag reports
- SQLAlchemy documentation
