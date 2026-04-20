# ADR 078: Data Migration from Access to PostgreSQL

## Metadata

- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: Development team
- **Drivers**: Access parity, repeatable ETL, referential integrity, PostgreSQL load safety
- **Tags**: migration, access, postgresql, etl, sqlalchemy

## Decision

Add in-repo migration helpers that translate Access-style source rows into ORM-ready PostgreSQL data, exclude Access replication columns, and order tables by foreign-key dependencies before loading.

## Context

The legacy application stores business data in Access `.accdb` files. The new PostgreSQL schema must accept the same data without manual one-off cleanup. Source field names often contain spaces or punctuation, Access replication metadata columns must be ignored, and parent tables must be loaded before dependent child tables.

## Alternatives Considered

### Manual export/import scripts only

- **Rejected**: too fragile for repeated migration runs and hard to test.

### Database-specific ETL tool

- **Rejected**: adds another dependency and obscures the project-specific mapping rules.

### Bulk copy without dependency ordering

- **Rejected**: risks foreign-key failures when child rows load before parent rows.

## Implementation Details

- Added `src/ith_webapp/services/access_migration.py`.
- Source column names are normalized to snake_case for lookup.
- ORM column attributes are populated when either the attribute name or mapped column name matches the normalized source field.
- Replication columns `s_guid`, `s_collineage`, `s_generation`, and `s_lineage` are skipped.
- Basic type coercion handles booleans, integers, numerics, and temporal values.
- Table load order uses SQLAlchemy metadata foreign-key sorting.

## Validation

- Added unit coverage for row normalization, type coercion, replication-column exclusion, and dependency ordering.
- Full test suite passes after the change.

## Consequences

### Positive

- Migration behavior is deterministic and testable.
- Source data cleanup is centralized in one helper module.
- Referential integrity is preserved by loading tables in dependency order.

### Negative

- Access-specific migration rules now live in application code and must be maintained.
- Additional source-specific coercions may still be needed for edge-case columns.

### Neutral

- The helpers support a future CLI or one-off ETL runner without committing to a specific runtime adapter yet.

## Monitoring & Rollback

- **Review date**: After the first real Access export is migrated
- **Success metrics**: source rows load without manual column cleanup, FK loads succeed, and downstream queries return expected counts
- **Rollback strategy**: remove the helper module and revert the related migration tests if the ETL shape changes materially

## References

- `src/ith_webapp/services/access_migration.py`
- `tests/unit/test_access_migration.py`
- `adr/001-2026-04-19-technology-selection.md`
- `adr/077-2026-04-20-production-postgresql-configuration.md`
