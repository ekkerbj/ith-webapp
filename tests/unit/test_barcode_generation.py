import pytest


@pytest.mark.parametrize(
    ("symbology", "value"),
    [
        ("code128", "ABC123"),
        ("code39", "ABC-123"),
        ("i2of5", "123456"),
        ("upca", "12345678901"),
        ("ean13", "123456789012"),
    ],
)
def test_generate_barcode_svg_returns_svg_bytes_for_supported_symbologies(symbology, value):
    from ith_webapp.services.barcode_generation import generate_barcode_svg

    svg_bytes = generate_barcode_svg(symbology, value)

    assert svg_bytes.startswith(b"<?xml")


def test_generate_pdf417_svg_returns_svg_bytes():
    from ith_webapp.services.barcode_generation import generate_pdf417_svg

    svg_bytes = generate_pdf417_svg("LABEL-123")

    assert svg_bytes.startswith(b"<?xml")
