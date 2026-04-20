# ADR 062: Customer-Specific Barcode Labels

## Metadata

- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: Development team
- **Drivers**: Replace Access customer-specific barcode labels, reuse deterministic SVG barcode generation, and keep packing-list-driven label output simple
- **Tags**: architecture, labels, packing-lists, barcode, html, printing
- **Supersedes**: None
- **Superseded By**: None

## Decision

The webapp will serve customer-specific barcode labels from the packing list workflow blueprint at `/packing-lists/<packing_list_id>/labels/cat` and `/packing-lists/<packing_list_id>/labels/zf`, rendering HTML label sheets with embedded Code128 barcode SVG output.

## Context

The Access application includes customer-specific label variants named CAT and ZF. The webapp already has deterministic SVG barcode generation and a packing list header model, so these labels can be rendered directly in HTML without introducing a separate PDF pipeline.

## Alternatives Considered

### Generate PDF labels

- **Pros**: Directly matches a print-oriented output format.
- **Cons**: Adds a separate rendering stack and more layout code.
- **Rejected**: HTML plus browser print styling is sufficient for the first migration.

### Store label templates in the database

- **Pros**: Could mirror the Access report catalog more closely.
- **Cons**: Adds schema and CRUD overhead for mostly static templates.
- **Rejected**: Code-driven templates are simpler and easier to extend.

### Create one generic label route with query parameters

- **Pros**: Fewer routes.
- **Cons**: CAT and ZF are distinct Access outputs and are clearer as dedicated endpoints.
- **Rejected**: Separate routes are more explicit and easier to map to legacy reports.

## Implementation Details

- Add CAT and ZF label routes to `src/ith_webapp/views/packing_list_workflow.py`.
- Load the packing list by ID and return 404 when it does not exist.
- Render the labels with `render_template_string()` to keep the first implementation self-contained.
- Reuse `generate_code128_svg()` with the packing list ID as the barcode payload.
- Include the packing list ID in the label body so the printed output is self-describing.

## Validation

- Added unit tests that verify both label routes return HTML containing the Access label names, packing list ID text, and embedded SVG barcode output.
- Verified the full test suite passes after implementation.

## Consequences

- **Positive**: Customer-specific labels are available without a new document subsystem.
- **Positive**: The output stays deterministic and reuses the shared barcode service.
- **Negative**: Browser print styling still carries the layout burden.
- **Neutral**: Additional customer label variants can be added as new routes or template variants later.

## Monitoring & Rollback

- **Review date**: When the mailing and address label work is implemented.
- **Success metrics**: CAT and ZF labels render correctly, remain easy to print, and map cleanly to the Access report names.
- **Rollback strategy**: Replace the HTML routes with a dedicated PDF or template-backed renderer if print fidelity requires it.

## References

- `src/ith_webapp/views/packing_list_workflow.py`
- `src/ith_webapp/services/barcode_generation.py`
- `tests/unit/test_packing_list_labels.py`
- `prd.json`
