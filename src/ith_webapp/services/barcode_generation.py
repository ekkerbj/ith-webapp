from __future__ import annotations

from barcode import get_barcode_class
from barcode.writer import SVGWriter

_BARCODE_CLASS_NAMES = {
    "code128": "code128",
    "code39": "code39",
    "i2of5": "itf",
    "itf": "itf",
    "upca": "upca",
    "ean13": "ean13",
}


def generate_barcode_svg(symbology: str, value: str) -> bytes:
    barcode_class_name = _BARCODE_CLASS_NAMES.get(symbology.lower())
    if barcode_class_name is None:
        raise ValueError(f"Unsupported barcode symbology: {symbology}")

    barcode_class = get_barcode_class(barcode_class_name)
    return barcode_class(value, writer=SVGWriter()).render(None)


def generate_code128_svg(value: str) -> bytes:
    return generate_barcode_svg("code128", value)


def generate_code39_svg(value: str) -> bytes:
    return generate_barcode_svg("code39", value)


def generate_interleaved_2of5_svg(value: str) -> bytes:
    return generate_barcode_svg("i2of5", value)


def generate_upca_svg(value: str) -> bytes:
    return generate_barcode_svg("upca", value)


def generate_ean13_svg(value: str) -> bytes:
    return generate_barcode_svg("ean13", value)
