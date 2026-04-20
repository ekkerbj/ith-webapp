# ADR 059: PDF417 Barcode Generation

## Metadata

- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: Development team
- **Drivers**: Replace Access PDF417 VBA helper, provide label-ready barcode output, keep implementation small and deterministic
- **Tags**: architecture, barcode, pdf417, svg, labels
- **Supersedes**: None
- **Superseded By**: None

## Decision

The webapp will generate PDF417 2D barcodes through a small service wrapper built on `pdf417gen`, returning SVG bytes for label and document rendering.

## Context

The Access application uses `IDAutomation_Native_PDF417_VBA.txt` for PDF417 barcodes. The webapp needs the same barcode family for labels without introducing a custom encoder or a heavyweight imaging pipeline.

## Alternatives Considered

### Custom PDF417 implementation

- **Pros**: No external dependency.
- **Cons**: High complexity and a large test surface.
- **Rejected**: Reinventing PDF417 encoding is unnecessary.

### ReportLab barcode rendering

- **Pros**: Possible integration with the existing PDF tooling.
- **Cons**: Larger dependency surface and more rendering glue.
- **Rejected**: A smaller dedicated PDF417 library better matches the narrow requirement.

## Implementation Details

- Add `pdf417gen` to project dependencies.
- Implement `generate_pdf417_svg()` in `src/ith_webapp/services/barcode_generation.py`.
- Encode the payload with `pdf417gen.encode()`.
- Convert the rendered SVG tree to UTF-8 XML bytes with the standard library.

## Validation

- Added a unit test that imports the new helper and verifies SVG bytes are returned.
- Verified the full test suite passes after the change.

## Consequences

- **Positive**: PDF417 generation stays deterministic and easy to embed in labels.
- **Positive**: The service mirrors the existing 1D barcode wrapper pattern.
- **Negative**: Consumers must handle SVG output rather than a raster image.
- **Neutral**: Future barcode families can be added by extending the same service module.

## Monitoring & Rollback

- **Review date**: When label-printing work is implemented.
- **Success metrics**: Label views and PDFs can reuse the helper without custom barcode logic.
- **Rollback strategy**: Replace the helper with another PDF417 backend if rendering requirements change.

## References

- `src/ith_webapp/services/barcode_generation.py`
- `tests/unit/test_barcode_generation.py`
- `pyproject.toml`
- `adr/058-2026-04-19-1d-barcode-generation.md`
