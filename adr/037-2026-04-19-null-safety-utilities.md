# ADR 037: Null Safety Utilities

## Metadata
- Date: 2026-04-19
- Status: Accepted
- Authors: The AI
- Drivers: F-037 backlog item, legacy calculation cleanup, prevention of null propagation in numeric logic
- Tags: utilities, null safety, calculations, coercion

## Decision
Add shared `Nnz(value)` and `Zero(number, keyword)` helpers in `src/ith_webapp/utils.py` for numeric coercion and conditional zeroing.

## Context
Legacy calculation code needs a consistent way to turn null and non-numeric inputs into `0` and to zero values only when a keyword explicitly requests it. Keeping that logic in one utility module avoids duplicating defensive checks across future pricing and measurement code.

## Alternatives Considered
- Inline conversion at each call site: rejected because it would duplicate rules and make later behavior changes expensive.
- A larger general-purpose math helper package: rejected because the backlog only requires two focused helpers and YAGNI applies.
- Model methods only: rejected because these helpers are cross-cutting and should be reusable outside a single model.

## Implementation Details
- Added `Nnz(value)` to return numeric inputs unchanged, coerce numeric strings to floats, and map null or non-numeric values to `0`.
- Added `Zero(number, keyword)` to return `0` when the keyword matches a zeroing token and otherwise return the original number.
- Added unit coverage in `tests/unit/test_null_safety.py`.

## Validation
- `pytest -q tests/unit/test_null_safety.py`
- `pytest -q`

## Consequences
- Future calculation code has a single place for null-safe numeric coercion.
- The helpers are small and easy to reuse, but the exact zeroing keywords must remain documented by tests.

## Monitoring & Rollback
- Review after the next calculation/back-office task uses the helpers in production code.
- Roll back by removing `src/ith_webapp/utils.py`, the related test, and this ADR if a different numeric utility convention replaces them.

## References
- `prd.json` F-037
- `src/ith_webapp/utils.py`
- `tests/unit/test_null_safety.py`
