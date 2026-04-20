# ADR 058: 1D Barcode Generation

## Metadata

- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: Development team
- **Drivers**: Replace Access VBA barcode functions, provide image output for labels/documents, keep implementation simple and testable
- **Tags**: architecture, barcode, svg, reporting

## Decision

The webapp will generate 1D barcodes through a small service wrapper built on `python-barcode`, returning SVG image bytes for Code128, Code39, Interleaved 2of5, UPC-A, and EAN13.

## Context

The Access application relies on IDAutomation VBA barcode helpers. The webapp needs the same barcode families for future labels and document outputs, but without introducing a raster-image pipeline or custom barcode renderer.

## Alternatives Considered

### Custom barcode renderer

- **Pros**: Full control over output format.
- **Cons**: High implementation risk, more code, harder to validate.
- **Rejected**: Reinventing barcode encoding is unnecessary.

### PNG/image generation with additional imaging dependencies

- **Pros**: Familiar for some document workflows.
- **Cons**: Extra dependency chain and less flexible embedding in HTML/PDF.
- **Rejected**: SVG is sufficient and simpler for the current reporting stack.

## Implementation Details

- Add `python-barcode` as a project dependency.
- Implement `ith_webapp.services.barcode_generation`.
- Normalize the requested symbology name to the library class name.
- Use `SVGWriter` and `render(None)` so the caller receives SVG bytes directly.
- Provide convenience wrappers for each supported barcode family.

## Validation

- Added unit coverage for all supported symbologies.
- Verified the full test suite passes after implementation.

## Consequences

- **Positive**: Barcodes are deterministic, lightweight, and easy to embed in future labels and reports.
- **Positive**: The service stays small and isolated.
- **Negative**: Output is SVG rather than PNG, so consumers must embed vector content or convert if they require raster images.
- **Neutral**: Additional barcode families can be added later by extending the mapping.

## Monitoring & Rollback

- **Review date**: After label printing work lands.
- **Success metrics**: Future label/report features can reuse the service without custom barcode logic.
- **Rollback strategy**: Replace the service wrapper with another barcode backend if embedding requirements change.

## References

- `src/ith_webapp/services/barcode_generation.py`
- `tests/unit/test_barcode_generation.py`
- `pyproject.toml`
- `adr/001-2026-04-19-technology-selection.md`
