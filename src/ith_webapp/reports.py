from __future__ import annotations

from decimal import Decimal

from flask import Blueprint, Response, current_app, request

from ith_webapp.models import Part, PartsList, PartsSub, Service, ServiceSub

bp = Blueprint("reports", __name__, url_prefix="/reports")


def _get_session():
    factory = current_app.config["SESSION_FACTORY"]
    return factory()


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _format_money(value) -> str:
    if value is None:
        return ""
    if isinstance(value, Decimal):
        return f"{value:.2f}"
    return f"{value:.2f}"


def _variant_label(region: str | None) -> str:
    variants = {"BR": "Brazil (-BR)", "MX": "Mexico (-MX)"}
    if not region:
        return "Standard"
    return variants.get(region.upper(), "Standard")


def _section_rows(subs: list[ServiceSub], item_types: set[str]) -> list[ServiceSub]:
    return [sub for sub in subs if (sub.item_type or "").upper() in item_types]


def _report_lines(service: Service, subs: list[ServiceSub], region: str | None) -> list[str]:
    lines = [
        "Service Multi Quote",
        f"Variant: {_variant_label(region)}",
        f"Customer: {getattr(service.customer, 'customer_name', '') or ''}",
        f"Card Code: {service.cardcode or ''}",
        f"Service ID: {service.service_id}",
        "",
    ]
    sections = [
        ("Fab Number Line Items", {"F", "I"}),
        ("Accessories", {"A"}),
        ("Sales Items", {"S", "L"}),
    ]
    for heading, item_types in sections:
        lines.append(heading)
        rows = _section_rows(subs, item_types)
        if not rows:
            lines.append("(none)")
        else:
            for sub in rows:
                lines.append(
                    " - "
                    f"Type {sub.item_type} | Qty {sub.quantity} | "
                    f"Price {_format_money(sub.price)} | Cost {_format_money(sub.cost)}"
                )
        lines.append("")
    lines.extend(
        [
            "Signature",
            "Prepared by: ____________________",
            "Date: ____________________________",
        ]
    )
    return lines


def _invoice_variant_label(variant: str | None) -> str:
    if variant and variant.lower() == "avatax":
        return "Avatax"
    return "Standard"


def _service_invoice_lines(
    service: Service, subs: list[ServiceSub], region: str | None, variant: str | None
) -> list[str]:
    lines = [
        "Service Invoice",
        f"Variant: {_variant_label(region)}",
        f"Tax Variant: {_invoice_variant_label(variant)}",
        f"Customer: {getattr(service.customer, 'customer_name', '') or ''}",
        f"Card Code: {service.cardcode or ''}",
        f"Service ID: {service.service_id}",
        f"Invoice Total: {_format_money(service.price)}",
        "",
    ]
    sections = [
        ("Fab Number Lines", {"F", "I"}),
        ("Accessories", {"A"}),
        ("Sales Lines", {"S", "L"}),
    ]
    for heading, item_types in sections:
        lines.append(heading)
        rows = _section_rows(subs, item_types)
        if not rows:
            lines.append("(none)")
        else:
            for sub in rows:
                lines.append(
                    " - "
                    f"Type {sub.item_type} | Qty {sub.quantity} | "
                    f"Price {_format_money(sub.price)} | Cost {_format_money(sub.cost)}"
                )
        lines.append("")
    return lines


def _basic_quote_lines(
    parts_list: PartsList,
    subs: list[PartsSub],
    parts_by_id: dict[int, Part],
    region: str | None,
) -> list[str]:
    lines = [
        "Basic Quote",
        f"Variant: {_variant_label(region)}",
        f"BOM: {parts_list.name or ''}",
        f"Quote ID: {parts_list.id}",
        "",
        "Bill of Materials",
    ]
    if not subs:
        lines.append("(none)")
    else:
        for sub in subs:
            part = parts_by_id.get(sub.part_id)
            part_number = part.part_number if part is not None else f"Part {sub.part_id}"
            description = part.description if part is not None and part.description else ""
            lines.append(
                f" - {part_number} | Qty {sub.quantity}"
                + (f" | {description}" if description else "")
            )
    lines.extend(
        [
            "",
            "Terms and Conditions",
            "Prices are subject to change without notice.",
            "Freight, duties, and taxes are extra unless stated.",
            "",
            "Why ITH",
            "Global support from a family-owned engineering team.",
            "Fast response and application expertise.",
            "",
            "Credit References",
            "Available upon request.",
        ]
    )
    return lines


def _paginate(lines: list[str], lines_per_page: int = 24) -> list[list[str]]:
    pages: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if len(current) >= lines_per_page:
            pages.append(current)
            current = []
        current.append(line)
    if current:
        pages.append(current)
    return pages or [["Service Multi Quote"]]


def _content_stream(lines: list[str]) -> bytes:
    text_ops = ["BT", "/F1 12 Tf", "14 TL", "72 760 Td"]
    first_line = True
    for line in lines:
        if not first_line:
            text_ops.append("T*")
        text_ops.append(f"({_escape_pdf_text(line)}) Tj")
        first_line = False
    text_ops.append("ET")
    return "\n".join(text_ops).encode("latin-1")


def _build_pdf(pages: list[list[str]]) -> bytes:
    object_count = 3 + len(pages) * 2
    objects: list[bytes | None] = [None] * object_count

    page_object_numbers: list[int] = []
    for index, page_lines in enumerate(pages):
        content_obj_num = 4 + index * 2
        page_obj_num = content_obj_num + 1
        page_object_numbers.append(page_obj_num)
        content_stream = _content_stream(page_lines)
        objects[content_obj_num - 1] = (
            f"<< /Length {len(content_stream)} >>\nstream\n".encode("latin-1")
            + content_stream
            + b"\nendstream"
        )
        objects[page_obj_num - 1] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_obj_num} 0 R >>"
        ).encode("latin-1")

    objects[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
    kids = " ".join(f"{page_obj_num} 0 R" for page_obj_num in page_object_numbers)
    objects[1] = (
        f"<< /Type /Pages /Kids [{kids}] /Count {len(page_object_numbers)} >>"
    ).encode("latin-1")
    objects[2] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"

    parts: list[bytes] = [b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"]
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        if body is None:
            raise RuntimeError(f"Missing PDF object {index}")
        offsets.append(sum(len(part) for part in parts))
        parts.append(f"{index} 0 obj\n".encode("latin-1") + body + b"\nendobj\n")
    xref_offset = sum(len(part) for part in parts)
    parts.append(f"xref\n0 {object_count + 1}\n".encode("latin-1"))
    parts.append(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        parts.append(f"{offset:010d} 00000 n \n".encode("latin-1"))
    parts.append(
        (
            "trailer\n"
            f"<< /Size {object_count + 1} /Root 1 0 R >>\n"
            "startxref\n"
            f"{xref_offset}\n"
            "%%EOF\n"
        ).encode("latin-1")
    )
    return b"".join(parts)


def build_service_multi_quote_pdf(session, service_id: int, region: str | None = None) -> bytes:
    service = session.get(Service, service_id)
    if service is None:
        raise ValueError(f"Service {service_id} not found")
    subs = (
        session.query(ServiceSub)
        .filter(ServiceSub.service_id == service_id)
        .order_by(ServiceSub.id)
        .all()
    )
    pages = _paginate(_report_lines(service, subs, region))
    return _build_pdf(pages)


def build_service_invoice_pdf(
    session, service_id: int, region: str | None = None, variant: str | None = None
) -> bytes:
    service = session.get(Service, service_id)
    if service is None:
        raise ValueError(f"Service {service_id} not found")
    subs = (
        session.query(ServiceSub)
        .filter(ServiceSub.service_id == service_id)
        .order_by(ServiceSub.id)
        .all()
    )
    pages = _paginate(_service_invoice_lines(service, subs, region, variant))
    return _build_pdf(pages)


def build_basic_quote_pdf(session, parts_list_id: int, region: str | None = None) -> bytes:
    parts_list = session.get(PartsList, parts_list_id)
    if parts_list is None:
        raise ValueError(f"PartsList {parts_list_id} not found")
    subs = (
        session.query(PartsSub)
        .filter(PartsSub.parts_list_id == parts_list_id)
        .order_by(PartsSub.id)
        .all()
    )
    part_ids = [sub.part_id for sub in subs]
    parts = (
        session.query(Part).filter(Part.part_id.in_(part_ids)).all() if part_ids else []
    )
    parts_by_id = {part.part_id: part for part in parts}
    pages = _paginate(_basic_quote_lines(parts_list, subs, parts_by_id, region))
    return _build_pdf(pages)


@bp.route("/service-multi-quote/<int:service_id>")
def service_multi_quote_report(service_id: int):
    session = _get_session()
    try:
        pdf_bytes = build_service_multi_quote_pdf(
            session, service_id, request.args.get("region")
        )
        response = Response(pdf_bytes, mimetype="application/pdf")
        response.headers["Content-Disposition"] = (
            f'inline; filename="service-multi-quote-{service_id}.pdf"'
        )
        return response
    finally:
        session.close()


@bp.route("/service-invoice/<int:service_id>")
def service_invoice_report(service_id: int):
    session = _get_session()
    try:
        pdf_bytes = build_service_invoice_pdf(
            session,
            service_id,
            request.args.get("region"),
            request.args.get("variant"),
        )
        response = Response(pdf_bytes, mimetype="application/pdf")
        response.headers["Content-Disposition"] = (
            f'inline; filename="service-invoice-{service_id}.pdf"'
        )
        return response
    finally:
        session.close()


@bp.route("/basic-quote/<int:parts_list_id>")
def basic_quote_report(parts_list_id: int):
    session = _get_session()
    try:
        pdf_bytes = build_basic_quote_pdf(session, parts_list_id, request.args.get("region"))
        response = Response(pdf_bytes, mimetype="application/pdf")
        response.headers["Content-Disposition"] = (
            f'inline; filename="basic-quote-{parts_list_id}.pdf"'
        )
        return response
    finally:
        session.close()
