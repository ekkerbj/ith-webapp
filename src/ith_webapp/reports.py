from __future__ import annotations

from datetime import date, datetime, time, timezone
from collections import defaultdict
from decimal import Decimal

from flask import Blueprint, Response, abort, current_app, render_template_string, request

from ith_webapp.models import (
    CheckIn,
    CheckInSub,
    AuditTrail,
    Customer,
    CustomerApplication,
    CustomerApplicationSpecs,
    ConsignmentList,
    CustomerTools,
    CustomerToolsSub,
    ITHTestGauge,
    FieldService,
    ServiceMeasurements,
    PackingList,
    PackingListSub,
    Part,
    PartsList,
    PartsSub,
    Rental,
    Service,
    ServiceSub,
    ServiceTime,
    Unit,
)

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


def _parts_catalog_context(session, part_id: int) -> dict[str, object]:
    part = session.get(Part, part_id)
    if part is None:
        raise ValueError(f"Part {part_id} not found")
    bom_rows = (
        session.query(PartsList, PartsSub)
        .join(PartsSub, PartsSub.parts_list_id == PartsList.id)
        .filter(PartsSub.part_id == part_id)
        .order_by(PartsList.id, PartsSub.id)
        .all()
    )
    cross_reference_rows = (
        session.query(ConsignmentList)
        .filter(ConsignmentList.part_id == part_id)
        .order_by(ConsignmentList.consignment_list_id)
        .all()
    )
    return {
        "part": part,
        "image_url": getattr(part, "image_url", "") or "",
        "bom_rows": [
            {
                "parts_list": parts_list,
                "quantity": sub.quantity,
            }
            for parts_list, sub in bom_rows
        ],
        "cross_reference_rows": [
            {
                "customer": row.customer,
                "quantity": row.quantity,
            }
            for row in cross_reference_rows
        ],
    }


_PARTS_CATALOG_TEMPLATE = """
{% extends "base.html" %}
{% block title %}Parts Catalog - ITH{% endblock %}
{% block content %}
<h1>Parts Catalog</h1>
<table>
  <tr><th>Part Number</th><td>{{ part.part_number }}</td></tr>
  <tr><th>Description</th><td>{{ part.description or "" }}</td></tr>
  <tr><th>Active</th><td>{{ "Yes" if part.active else "No" }}</td></tr>
</table>
<section>
  <h2>Item Image</h2>
  {% if image_url %}
  <p>{{ image_url }}</p>
  {% else %}
  <p>No image on file.</p>
  {% endif %}
</section>
<section>
  <h2>Bill of Materials</h2>
  {% if bom_rows %}
  <ul>
    {% for row in bom_rows %}
    <li>{{ row.parts_list.name }} | Qty {{ row.quantity }}</li>
    {% endfor %}
  </ul>
  {% else %}
  <p>(none)</p>
  {% endif %}
</section>
<section>
  <h2>Customer Cross-References</h2>
  {% if cross_reference_rows %}
  <ul>
    {% for row in cross_reference_rows %}
    <li>{{ row.customer.customer_name }}{% if row.customer.card_code %} | {{ row.customer.card_code }}{% endif %} | Qty {{ row.quantity }}</li>
    {% endfor %}
  </ul>
  {% else %}
  <p>(none)</p>
  {% endif %}
</section>
{% endblock %}
"""


def _parts_catalog_lines(context: dict[str, object]) -> list[str]:
    part = context["part"]
    lines = [
        "Parts Catalog",
        f"Part Number: {part.part_number}",
        f"Description: {part.description or ''}",
        f"Active: {'Yes' if part.active else 'No'}",
        "",
        "Item Image",
    ]
    image_url = context["image_url"]
    lines.append(image_url if image_url else "No image on file.")
    lines.extend(["", "Bill of Materials"])
    bom_rows = context["bom_rows"]
    if not bom_rows:
        lines.append("(none)")
    else:
        for row in bom_rows:
            lines.append(f" - {row['parts_list'].name} | Qty {row['quantity']}")
    lines.extend(["", "Customer Cross-References"])
    cross_reference_rows = context["cross_reference_rows"]
    if not cross_reference_rows:
        lines.append("(none)")
    else:
        for row in cross_reference_rows:
            customer = row["customer"]
            label = customer.customer_name
            if customer.card_code:
                label += f" | {customer.card_code}"
            lines.append(f" - {label} | Qty {row['quantity']}")
    return lines


def _packing_list_lines(packing_list: PackingList, subs: list[PackingListSub]) -> list[str]:
    lines = [
        "Packing List",
        f"Packing List ID: {packing_list.id}",
        "",
        "Line Items",
    ]
    if not subs:
        lines.append("(none)")
    else:
        for sub in subs:
            lines.extend(
                [
                    f"Line {sub.id}",
                    f"Harm Number: {sub.harm_number or ''}",
                    f"EECN: {sub.EECN or ''}",
                    f"DDTC: {sub.DDTC or ''}",
                    f"COO: {sub.COO or ''}",
                    f"In Bond Code: {sub.in_bond_code or ''}",
                    "",
            ]
        )
    return lines


def _commercial_invoice_and_sli_lines(
    packing_list: PackingList, subs: list[PackingListSub]
) -> list[str]:
    lines = [
        "Commercial Invoice",
        f"Packing List ID: {packing_list.id}",
        "",
        "Shipper's Letter of Instruction",
        "Export Compliance",
    ]
    if not subs:
        lines.append("(none)")
    else:
        for sub in subs:
            lines.extend(
                [
                    f"Line {sub.id}",
                    f"Harm Number: {sub.harm_number or ''}",
                    f"EECN: {sub.EECN or ''}",
                    f"DDTC: {sub.DDTC or ''}",
                    f"COO: {sub.COO or ''}",
                    f"In Bond Code: {sub.in_bond_code or ''}",
                    "",
                ]
            )
    return lines


def _check_in_lines(check_in: CheckIn, subs: list[CheckInSub]) -> list[str]:
    lines = [
        "Check In Document",
        "Tool Receipt Record",
        f"Customer: {getattr(check_in.customer, 'customer_name', '') or ''}",
        f"Received: {check_in.received_at.isoformat()}",
        f"Description: {check_in.description or ''}",
        "",
        "Tools Received",
    ]
    if not subs:
        lines.append("(none)")
    else:
        for sub in subs:
            lines.append(
                " - "
                f"Tool {sub.tool_id} | Inspected {'Yes' if sub.inspected else 'No'} | "
                f"Quoted {'Yes' if sub.quoted else 'No'} | "
                f"Approved {'Yes' if sub.approved else 'No'} | "
                f"Closed {'Yes' if sub.closed else 'No'}"
            )
    return lines


def _certificate_variant_label(variant: str | None) -> str:
    if variant and variant.lower() == "iso17025":
        return "ISO 17025"
    return "Standard"


def _ith_test_gauge_certificate_lines(
    gauge: ITHTestGauge, certificate_title: str, variant: str | None
) -> list[str]:
    return [
        certificate_title,
        f"Variant: {_certificate_variant_label(variant)}",
        f"Gauge Name: {gauge.name or ''}",
        f"Serial Number: {gauge.serial_number}",
        f"Type: {getattr(gauge.ith_test_gauge_type, 'name', '') or ''}",
        f"Calibration Due: {gauge.calibration_due_date or ''}",
        f"Certification Due: {gauge.certification_due_date or ''}",
        "",
        "Certificate Statement",
        "This document certifies the gauge for the stated test type.",
    ]


def _measurement_display_value(value) -> str:
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return _format_money(value) if value is not None else ""


def _service_measurement_lines(
    service: Service,
    measurement: ServiceMeasurements,
    title: str,
    tool_name: str,
    label: str,
    value,
) -> list[str]:
    lines = [
        title,
        f"Tool Type: {tool_name}",
        f"Customer: {getattr(service.customer, 'customer_name', '') or ''}",
        f"Card Code: {service.cardcode or ''}",
        f"Service ID: {service.service_id}",
        "",
        label,
        f"Value: {_measurement_display_value(value)}",
    ]
    if title.endswith("Test Report"):
        lines.extend(
            [
                "",
                "Test Result",
                f"Pass/Fail: {_measurement_display_value(measurement.btc_passed)}",
            ]
        )
    return lines


def _service_measurement_report_pages(
    service: Service, measurement: ServiceMeasurements
) -> list[list[str]]:
    specs = [
        ("BTC", "btc_passed", "Pass/Fail"),
        ("Gauge", "gauge_value", "Gauge Value"),
        ("Hose", "hose_pressure", "Hose Pressure"),
        ("Nut Runner", "nut_runner_torque", "Nut Runner Torque"),
        ("Pump", "pump_output", "Pump Output"),
        ("Torque Wrench", "torque_wrench_setting", "Torque Wrench Setting"),
    ]
    pages: list[list[str]] = []
    for tool_name, field_name, label in specs:
        value = getattr(measurement, field_name)
        pages.append(
            _service_measurement_lines(
                service, measurement, f"{tool_name} Measurement Form", tool_name, label, value
            )
        )
        pages.append(
            _service_measurement_lines(
                service, measurement, f"{tool_name} Test Report", tool_name, label, value
            )
        )
    return pages


def _field_service_time_rows(session, customer_id: int) -> list[tuple[ServiceTime, Service]]:
    return (
        session.query(ServiceTime, Service)
        .join(Service, Service.service_id == ServiceTime.service_id)
        .filter(Service.customer_id == customer_id)
        .order_by(ServiceTime.date, ServiceTime.id)
        .all()
    )


def _field_service_decimal_total(rows, field_name: str) -> Decimal:
    total = Decimal("0")
    for row in rows:
        value = getattr(row[0], field_name)
        if value is not None:
            total += Decimal(str(value))
    return total


def _field_service_lines(
    field_service: FieldService,
    title: str,
    rows: list[tuple[ServiceTime, Service]],
    customer_facing: bool = False,
) -> list[str]:
    customer_name = getattr(field_service.customer, "customer_name", "") or ""
    status_name = getattr(field_service.field_service_status, "name", "") or ""
    total_hours = _field_service_decimal_total(rows, "hours")
    total_amount = Decimal("0")
    for time_entry, _service in rows:
        hours = Decimal(str(time_entry.hours))
        rate = Decimal(str(time_entry.labor_rate))
        total_amount += hours * rate

    lines = [
        title,
        f"Customer: {customer_name}",
        f"Status: {status_name}",
        f"Visit Date: {field_service.visit_date.isoformat()}",
        f"Notes: {field_service.visit_notes or ''}",
        "",
    ]
    if "Summary" in title:
        lines.extend(
            [
                "Summary",
                f"Service Entries: {len(rows)}",
                f"Total Hours: {total_hours:.2f}",
                f"Total Labor: {total_amount:.2f}",
            ]
        )
        return lines

    lines.append("Time Entries")
    if not rows:
        lines.append("(none)")
        return lines

    for time_entry, service in rows:
        hours = Decimal(str(time_entry.hours))
        rate = Decimal(str(time_entry.labor_rate))
        if customer_facing:
            lines.append(
                " - "
                f"Service {service.service_id} | "
                f"{time_entry.date} | "
                f"Technician {time_entry.technician} | "
                f"Hours {hours:.2f}"
            )
        else:
            lines.append(
                " - "
                f"Service {service.service_id} | "
                f"{time_entry.date} | "
                f"Technician {time_entry.technician} | "
                f"Hours {hours:.2f} | "
                f"Rate {rate:.2f} | "
                f"Amount {(hours * rate):.2f}"
            )
    lines.extend(
        [
            "",
            f"Total Hours: {total_hours:.2f}",
        ]
    )
    if not customer_facing:
        lines.append(f"Total Labor: {total_amount:.2f}")
    return lines


def build_field_service_report_pdf(session, field_service_id: int) -> bytes:
    field_service = session.get(FieldService, field_service_id)
    if field_service is None:
        raise ValueError(f"FieldService {field_service_id} not found")
    rows = _field_service_time_rows(session, field_service.customer_id)
    pages = _paginate(_field_service_lines(field_service, "Field Service Report", rows))
    return _build_pdf(pages)


def build_field_service_summary_pdf(session, field_service_id: int) -> bytes:
    field_service = session.get(FieldService, field_service_id)
    if field_service is None:
        raise ValueError(f"FieldService {field_service_id} not found")
    rows = _field_service_time_rows(session, field_service.customer_id)
    pages = _paginate(_field_service_lines(field_service, "Field Service Summary", rows))
    return _build_pdf(pages)


def build_field_service_timesheet_pdf(
    session, field_service_id: int, customer_facing: bool = False
) -> bytes:
    field_service = session.get(FieldService, field_service_id)
    if field_service is None:
        raise ValueError(f"FieldService {field_service_id} not found")
    rows = _field_service_time_rows(session, field_service.customer_id)
    title = "Customer-facing Timesheet" if customer_facing else "Timesheet"
    pages = _paginate(_field_service_lines(field_service, title, rows, customer_facing))
    return _build_pdf(pages)


def _customer_detail_context(session, customer_id: int) -> dict[str, object]:
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise ValueError(f"Customer {customer_id} not found")
    applications = (
        session.query(CustomerApplication)
        .filter(CustomerApplication.customer_id == customer_id)
        .order_by(CustomerApplication.id)
        .all()
    )
    tools = (
        session.query(CustomerTools)
        .filter(CustomerTools.customer_id == customer_id)
        .order_by(CustomerTools.id)
        .all()
    )
    return {
        "customer": customer,
        "markets": [market.name for market in customer.markets],
        "applications": [
            {
                "application": application,
                "specs": (
                    session.query(CustomerApplicationSpecs)
                    .filter(CustomerApplicationSpecs.application_id == application.id)
                    .order_by(CustomerApplicationSpecs.id)
                    .all()
                ),
            }
            for application in applications
        ],
        "tools": [
            {
                "tool": tool,
                "unit": session.get(Unit, tool.unit_id) if tool.unit_id is not None else None,
            }
            for tool in tools
        ],
    }


def _customer_region_groups(session) -> list[dict[str, object]]:
    customers = session.query(Customer).order_by(Customer.customer_name).all()
    groups: dict[str, list[Customer]] = defaultdict(list)
    for customer in customers:
        if customer.markets:
            for market in customer.markets:
                groups[market.name].append(customer)
        else:
            groups["Unassigned"].append(customer)
    return [
        {"name": name, "customers": rows}
        for name, rows in sorted(groups.items(), key=lambda item: item[0])
    ]


def _customer_responsibility_groups(session) -> list[dict[str, object]]:
    customers = session.query(Customer).order_by(Customer.customer_name).all()
    groups: dict[str, list[Customer]] = defaultdict(list)
    for customer in customers:
        label = (
            f"Responsibility {customer.responsibility_id}"
            if customer.responsibility_id is not None
            else "Unassigned"
        )
        groups[label].append(customer)
    return [
        {"name": name, "customers": rows}
        for name, rows in sorted(groups.items(), key=lambda item: item[0])
    ]


def _customer_pricing_rows(session) -> list[dict[str, object]]:
    customer_repository = current_app.config.get("SAP_CUSTOMER_REPOSITORY")
    item_repository = current_app.config.get("SAP_ITEM_REPOSITORY")
    price_repository = current_app.config.get("SAP_PRICE_REPOSITORY")

    customers = session.query(Customer).order_by(Customer.customer_name).all()
    parts = session.query(Part).order_by(Part.part_number).all()
    if customer_repository is None or item_repository is None or price_repository is None:
        return [
            {
                "customer_name": customer.customer_name or "",
                "card_code": customer.card_code or "",
                "price_list_num": customer.price_list_num,
                "multiplier": customer.multiplier,
                "active": customer.active,
                "item_code": "",
                "item_name": "",
                "standard_price": None,
                "specific_price": None,
                "integrity": "",
            }
            for customer in customers
        ]

    rows: list[dict[str, object]] = []
    for customer in customers:
        card_code = customer.card_code or ""
        customer_record = (
            customer_repository.get_customer(card_code) if card_code else None
        )
        for part in parts:
            item_code = part.part_number
            item_record = item_repository.get_item(item_code)
            standard_price = (
                price_repository.get_price_list_price(customer.price_list_num, item_code)
                if customer.price_list_num is not None
                else None
            )
            specific_price = (
                price_repository.get_bp_price(card_code, item_code) if card_code else None
            )
            if specific_price is None and standard_price is None:
                continue
            rows.append(
                {
                    "customer_name": (
                        getattr(customer_record, "card_name", None)
                        or customer.customer_name
                        or ""
                    ),
                    "card_code": card_code,
                    "price_list_num": customer.price_list_num,
                    "multiplier": customer.multiplier,
                    "active": customer.active,
                    "item_code": getattr(item_record, "item_code", None) or item_code,
                    "item_name": getattr(item_record, "item_name", None)
                    or part.description
                    or "",
                    "standard_price": standard_price,
                    "specific_price": specific_price,
                    "integrity": _customer_pricing_integrity(
                        specific_price, standard_price
                    ),
                }
            )
    return rows


def _customer_pricing_integrity(
    specific_price: Decimal | None, standard_price: Decimal | None
) -> str:
    if specific_price is None and standard_price is None:
        return "Missing"
    if specific_price is None:
        return "Standard only"
    if standard_price is None:
        return "Specific only"
    return "OK" if specific_price <= standard_price else "Check"


def _customer_tools_rows(session) -> list[dict[str, object]]:
    rows = (
        session.query(CustomerTools)
        .order_by(CustomerTools.id)
        .all()
    )
    return [
        {
            "customer": row.customer,
            "tool": row,
            "unit": session.get(Unit, row.unit_id) if row.unit_id is not None else None,
        }
        for row in rows
    ]


def _customer_tools_detail_lines(
    tool: CustomerTools, unit: Unit | None, subs: list[CustomerToolsSub]
) -> list[str]:
    lines = [
        "Toolset Detail Report",
        f"Customer: {getattr(tool.customer, 'customer_name', '') or ''}",
        f"Serial Number: {tool.serial_number or ''}",
        f"Fab Number: {tool.fab_number or ''}",
        f"Model: {tool.model_info or ''}",
        f"Unit: {unit.name if unit else ''}",
        "",
        "Component List",
    ]
    if not subs:
        lines.append("(none)")
    else:
        for sub in subs:
            lines.append(
                f" - {sub.sub_type or ''}"
                + (f" | {sub.value}" if sub.value else "")
            )
    return lines


def _open_repair_list_rows(session) -> list[dict[str, object]]:
    rows = (
        session.query(CheckInSub, CheckIn, Customer)
        .join(CheckIn, CheckIn.id == CheckInSub.check_in_id)
        .join(Customer, Customer.customer_id == CheckIn.customer_id)
        .filter(CheckInSub.closed.is_(False))
        .order_by(CheckIn.received_at, CheckIn.id, CheckInSub.id)
        .all()
    )
    return [
        {"sub": sub, "check_in": check_in, "customer": customer}
        for sub, check_in, customer in rows
    ]


def _shop_data_rows(session) -> list[dict[str, object]]:
    rows = (
        session.query(ServiceTime, Service, Customer)
        .join(Service, Service.service_id == ServiceTime.service_id)
        .join(Customer, Customer.customer_id == Service.customer_id)
        .order_by(ServiceTime.date, ServiceTime.id)
        .all()
    )
    summary: dict[str, dict[str, object]] = {}
    for time_entry, service, _customer in rows:
        technician = time_entry.technician or "Unassigned"
        row = summary.setdefault(
            technician,
            {
                "technician": technician,
                "status_set": set(),
                "service_ids": set(),
                "total_hours": Decimal("0"),
                "total_labor": Decimal("0"),
            },
        )
        row["status_set"].add(service.order_status or "Unassigned")
        row["service_ids"].add(service.service_id)
        row["total_hours"] += Decimal(str(time_entry.hours))
        row["total_labor"] += Decimal(str(time_entry.hours)) * Decimal(
            str(time_entry.labor_rate)
        )
    return [
        {
            "technician": row["technician"],
            "statuses": sorted(row["status_set"]),
            "service_count": len(row["service_ids"]),
            "total_hours": f"{row['total_hours']:.2f}",
            "total_labor": f"{row['total_labor']:.2f}",
        }
        for row in sorted(summary.values(), key=lambda item: item["technician"])
    ]


def _repair_time_analysis_rows(session) -> list[dict[str, object]]:
    rows = (
        session.query(ServiceTime, Service, Customer)
        .join(Service, Service.service_id == ServiceTime.service_id)
        .join(Customer, Customer.customer_id == Service.customer_id)
        .order_by(Customer.customer_name, Service.service_id, ServiceTime.technician, ServiceTime.id)
        .all()
    )
    summary: dict[tuple[int, str], dict[str, object]] = {}
    for time_entry, service, customer in rows:
        technician = time_entry.technician or "Unassigned"
        key = (service.service_id, technician)
        row = summary.setdefault(
            key,
            {
                "customer_name": customer.customer_name or "",
                "service_id": service.service_id,
                "technician": technician,
                "entry_count": 0,
                "total_hours": Decimal("0"),
                "total_labor": Decimal("0"),
            },
        )
        row["entry_count"] += 1
        row["total_hours"] += Decimal(str(time_entry.hours))
        row["total_labor"] += Decimal(str(time_entry.hours)) * Decimal(str(time_entry.labor_rate))
    return [
        {
            "customer_name": row["customer_name"],
            "service_id": row["service_id"],
            "technician": row["technician"],
            "entry_count": row["entry_count"],
            "total_hours": f"{row['total_hours']:.2f}",
            "total_labor": f"{row['total_labor']:.2f}",
        }
        for row in summary.values()
    ]


def _parse_audit_trail_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        abort(400, description=f"Invalid audit trail date: {value}")


def _audit_trail_rows(session) -> list[AuditTrail]:
    query = session.query(AuditTrail)
    entity = (request.args.get("entity") or "").strip()
    field = (request.args.get("field") or "").strip()
    user = (request.args.get("user") or "").strip()
    if entity:
        query = query.filter(AuditTrail.table_name == entity)
    if field:
        query = query.filter(AuditTrail.field_name == field)
    if user:
        query = query.filter(AuditTrail.changed_by == user)

    start_date = _parse_audit_trail_date(request.args.get("start_date"))
    end_date = _parse_audit_trail_date(request.args.get("end_date"))
    if start_date is not None:
        query = query.filter(
            AuditTrail.changed_at >= datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        )
    if end_date is not None:
        query = query.filter(
            AuditTrail.changed_at <= datetime.combine(end_date, time.max, tzinfo=timezone.utc)
        )
    return query.order_by(AuditTrail.changed_at.desc(), AuditTrail.audit_trail_id.desc()).all()


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


_OPEN_REPAIR_LIST_TEMPLATE = """
{% extends "base.html" %}
{% block title %}Open Repair List - ITH{% endblock %}
{% block content %}
<h1>Open Repair List</h1>
<table>
  <thead>
    <tr><th>Customer</th><th>Received</th><th>Tool</th><th>Inspected</th><th>Quoted</th><th>Approved</th></tr>
  </thead>
  <tbody>
    {% if rows %}
    {% for row in rows %}
    <tr>
      <td>{{ row.customer.customer_name }}</td>
      <td>{{ row.check_in.received_at.isoformat() }}</td>
      <td>Tool {{ row.sub.tool_id }}</td>
      <td>{{ "Yes" if row.sub.inspected else "No" }}</td>
      <td>{{ "Yes" if row.sub.quoted else "No" }}</td>
      <td>{{ "Yes" if row.sub.approved else "No" }}</td>
    </tr>
    {% endfor %}
    {% else %}
    <tr><td colspan="6">(none)</td></tr>
    {% endif %}
  </tbody>
</table>
{% endblock %}
"""


_SHOP_DATA_TEMPLATE = """
{% extends "base.html" %}
{% block title %}ITH Shop Data - ITH{% endblock %}
{% block content %}
<h1>ITH Shop Data</h1>
<table>
  <thead>
    <tr><th>Technician</th><th>Statuses</th><th>Services</th><th>Total Hours</th><th>Total Labor</th></tr>
  </thead>
  <tbody>
    {% if rows %}
    {% for row in rows %}
    <tr>
      <td>{{ row.technician }}</td>
      <td>{{ row.statuses | join(", ") }}</td>
      <td>{{ row.service_count }}</td>
      <td>{{ row.total_hours }}</td>
      <td>{{ row.total_labor }}</td>
    </tr>
    {% endfor %}
    {% else %}
    <tr><td colspan="5">(none)</td></tr>
    {% endif %}
  </tbody>
</table>
{% endblock %}
"""

_AUDIT_TRAIL_TEMPLATE = """
{% extends "base.html" %}
{% block title %}Audit Trail Report - ITH{% endblock %}
{% block content %}
<h1>Audit Trail Report</h1>
<form method="get">
  <label>Entity <input type="text" name="entity" value="{{ entity }}"></label>
  <label>Field <input type="text" name="field" value="{{ field }}"></label>
  <label>User <input type="text" name="user" value="{{ user }}"></label>
  <label>Start Date <input type="date" name="start_date" value="{{ start_date }}"></label>
  <label>End Date <input type="date" name="end_date" value="{{ end_date }}"></label>
  <button type="submit">Filter</button>
</form>
<table>
  <thead>
    <tr>
      <th>Entity</th>
      <th>Record</th>
      <th>Action</th>
      <th>Field</th>
      <th>User</th>
      <th>Old Value</th>
      <th>New Value</th>
      <th>Changed At</th>
    </tr>
  </thead>
  <tbody>
    {% if entries %}
    {% for entry in entries %}
    <tr>
      <td>{{ entry.table_name }}</td>
      <td>{{ entry.record_id }}</td>
      <td>{{ entry.action }}</td>
      <td>{{ entry.field_name }}</td>
      <td>{{ entry.changed_by or "" }}</td>
      <td>{{ entry.old_value or "" }}</td>
      <td>{{ entry.new_value or "" }}</td>
      <td>{{ entry.changed_at }}</td>
    </tr>
    {% endfor %}
    {% else %}
    <tr><td colspan="7">(none)</td></tr>
    {% endif %}
  </tbody>
</table>
{% endblock %}
"""

_REPAIR_TIME_ANALYSIS_TEMPLATE = """
{% extends "base.html" %}
{% block title %}Repair Time Analysis - ITH{% endblock %}
{% block content %}
<h1>Repair Time Analysis</h1>
<table>
  <thead>
    <tr><th>Customer</th><th>Service</th><th>Technician</th><th>Entries</th><th>Total Hours</th><th>Total Labor</th></tr>
  </thead>
  <tbody>
    {% if rows %}
    {% for row in rows %}
    <tr>
      <td>{{ row.customer_name }}</td>
      <td>{{ row.service_id }}</td>
      <td>{{ row.technician }}</td>
      <td>{{ row.entry_count }}</td>
      <td>{{ row.total_hours }}</td>
      <td>{{ row.total_labor }}</td>
    </tr>
    {% endfor %}
    {% else %}
    <tr><td colspan="6">(none)</td></tr>
    {% endif %}
  </tbody>
</table>
{% endblock %}
"""


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


def build_parts_catalog_pdf(session, part_id: int) -> bytes:
    pages = _paginate(_parts_catalog_lines(_parts_catalog_context(session, part_id)))
    return _build_pdf(pages)


def build_packing_list_pdf(session, packing_list_id: int) -> bytes:
    packing_list = session.get(PackingList, packing_list_id)
    if packing_list is None:
        raise ValueError(f"PackingList {packing_list_id} not found")
    subs = (
        session.query(PackingListSub)
        .filter(PackingListSub.packing_list_id == packing_list_id)
        .order_by(PackingListSub.id)
        .all()
    )
    pages = _paginate(_packing_list_lines(packing_list, subs))
    return _build_pdf(pages)


def build_commercial_invoice_and_sli_pdf(session, packing_list_id: int) -> bytes:
    packing_list = session.get(PackingList, packing_list_id)
    if packing_list is None:
        raise ValueError(f"PackingList {packing_list_id} not found")
    subs = (
        session.query(PackingListSub)
        .filter(PackingListSub.packing_list_id == packing_list_id)
        .order_by(PackingListSub.id)
        .all()
    )
    pages = _paginate(_commercial_invoice_and_sli_lines(packing_list, subs))
    return _build_pdf(pages)


def build_check_in_pdf(session, check_in_id: int) -> bytes:
    check_in = session.get(CheckIn, check_in_id)
    if check_in is None:
        raise ValueError(f"CheckIn {check_in_id} not found")
    subs = (
        session.query(CheckInSub)
        .filter(CheckInSub.check_in_id == check_in_id)
        .order_by(CheckInSub.id)
        .all()
    )
    pages = _paginate(_check_in_lines(check_in, subs))
    return _build_pdf(pages)


def _demo_contract_lines(contract: Rental) -> list[str]:
    lines = [
        "Demo Contract",
        f"Customer: {getattr(contract.customer, 'customer_name', '') or ''}",
        f"Card Code: {getattr(contract.customer, 'card_code', '') or ''}",
        f"Tool: {getattr(contract.customer_tools, 'serial_number', '') or ''}",
        f"Status: {getattr(contract.rental_status, 'name', '') or ''}",
        f"Contract Date: {contract.rental_date.isoformat()}",
        f"Return Date: {contract.return_date.isoformat() if contract.return_date else ''}",
        "",
        "Agreement",
        "Customer accepts responsibility for the demo equipment during the loan period.",
        "",
        "Signature",
        "Customer Signature: ____________________",
        "ITH Representative: ____________________",
    ]
    return lines


def build_demo_contract_pdf(session, demo_contract_id: int) -> bytes:
    contract = session.get(Rental, demo_contract_id)
    if contract is None:
        raise ValueError(f"Rental {demo_contract_id} not found")
    pages = _paginate(_demo_contract_lines(contract))
    return _build_pdf(pages)


def build_ith_test_gauge_certificates_pdf(
    session, ith_test_gauge_id: int, variant: str | None = None
) -> bytes:
    gauge = session.get(ITHTestGauge, ith_test_gauge_id)
    if gauge is None:
        raise ValueError(f"ITHTestGauge {ith_test_gauge_id} not found")
    pages = [
        _ith_test_gauge_certificate_lines(gauge, title, variant)
        for title in (
            "Gauge Calibration Certificate",
            "Force Test Certificate",
            "Torque Test Certificate",
        )
    ]
    return _build_pdf(pages)


def build_service_measurements_pdf(session, service_id: int) -> bytes:
    service = session.get(Service, service_id)
    if service is None:
        raise ValueError(f"Service {service_id} not found")
    measurement = (
        session.query(ServiceMeasurements)
        .filter(ServiceMeasurements.service_id == service_id)
        .order_by(ServiceMeasurements.id)
        .first()
    )
    if measurement is None:
        raise ValueError(f"ServiceMeasurements for service {service_id} not found")
    pages = _service_measurement_report_pages(service, measurement)
    return _build_pdf(pages)


def build_customer_tools_pdf(session, customer_tools_id: int) -> bytes:
    tool = session.get(CustomerTools, customer_tools_id)
    if tool is None:
        raise ValueError(f"CustomerTools {customer_tools_id} not found")
    subs = (
        session.query(CustomerToolsSub)
        .filter(CustomerToolsSub.tool_id == customer_tools_id)
        .order_by(CustomerToolsSub.id)
        .all()
    )
    unit = session.get(Unit, tool.unit_id) if tool.unit_id is not None else None
    pages = _paginate(_customer_tools_detail_lines(tool, unit, subs))
    return _build_pdf(pages)


@bp.route("/parts/<int:part_id>")
def parts_catalog_report(part_id: int):
    session = _get_session()
    try:
        context = _parts_catalog_context(session, part_id)
        return render_template_string(_PARTS_CATALOG_TEMPLATE, **context)
    finally:
        session.close()


@bp.route("/parts/<int:part_id>/pdf")
def parts_catalog_pdf_report(part_id: int):
    session = _get_session()
    try:
        pdf_bytes = build_parts_catalog_pdf(session, part_id)
        response = Response(pdf_bytes, mimetype="application/pdf")
        response.headers["Content-Disposition"] = (
            f'inline; filename="parts-catalog-{part_id}.pdf"'
        )
        return response
    finally:
        session.close()


_CUSTOMER_DETAIL_TEMPLATE = """
{% extends "base.html" %}
{% block title %}Customer Report - ITH{% endblock %}
{% block content %}
<h1>Customer Report</h1>
<table>
  <tr><th>Name</th><td>{{ customer.customer_name or "" }}</td></tr>
  <tr><th>Card Code</th><td>{{ customer.card_code or "" }}</td></tr>
  <tr><th>Active</th><td>{{ "Yes" if customer.active else "No" }}</td></tr>
  <tr><th>Website</th><td>{{ customer.website or "" }}</td></tr>
  <tr><th>Comments</th><td>{{ customer.comments or "" }}</td></tr>
</table>
<section>
  <h2>Markets</h2>
  {% if markets %}
  <ul>{% for market in markets %}<li>{{ market }}</li>{% endfor %}</ul>
  {% else %}<p>No markets assigned.</p>{% endif %}
</section>
<section>
  <h2>Applications</h2>
  {% if applications %}
  {% for item in applications %}
  <h3>{{ item.application.name }}</h3>
  <p>{{ item.application.description or "" }}</p>
  {% if item.specs %}
  <ul>{% for spec in item.specs %}<li>{{ spec.key }}: {{ spec.value or "" }}</li>{% endfor %}</ul>
  {% endif %}
  {% endfor %}
  {% else %}<p>No applications assigned.</p>{% endif %}
</section>
<section>
  <h2>Tools</h2>
  {% if tools %}
  <ul>
    {% for item in tools %}
    <li>{{ item.tool.serial_number }}{% if item.tool.fab_number %} | {{ item.tool.fab_number }}{% endif %}{% if item.unit %} | {{ item.unit.name }}{% endif %}</li>
    {% endfor %}
  </ul>
  {% else %}<p>No tools assigned.</p>{% endif %}
</section>
{% endblock %}
"""

_CUSTOMER_GROUP_TEMPLATE = """
{% extends "base.html" %}
{% block title %}{{ title }} - ITH{% endblock %}
{% block content %}
<h1>{{ title }}</h1>
{% for group in groups %}
<section>
  <h2>{{ group.name }}</h2>
  <ul>{% for customer in group.customers %}<li>{{ customer.customer_name }}</li>{% endfor %}</ul>
</section>
{% endfor %}
{% endblock %}
"""

_CUSTOMER_PRICING_TEMPLATE = """
{% extends "base.html" %}
{% block title %}Customer Pricing Report - ITH{% endblock %}
{% block content %}
<h1>Customer Pricing Report</h1>
<table>
  <thead>
    <tr>
      <th>Customer</th>
      <th>Card Code</th>
      <th>Price List</th>
      <th>Multiplier</th>
      <th>Active</th>
      <th>Item</th>
      <th>Standard Price (ITM1)</th>
      <th>Customer Specific Price (OSPP)</th>
      <th>Price Integrity</th>
    </tr>
  </thead>
  <tbody>
    {% for row in customers %}
    <tr>
      <td>{{ row.customer_name }}</td>
      <td>{{ row.card_code }}</td>
      <td>{{ row.price_list_num or "" }}</td>
      <td>{{ row.multiplier or "" }}</td>
      <td>{{ "Yes" if row.active else "No" if row.active is not none else "" }}</td>
      <td>{{ row.item_code }}{% if row.item_name %} | {{ row.item_name }}{% endif %}</td>
      <td>{{ row.standard_price if row.standard_price is not none else "" }}</td>
      <td>{{ row.specific_price if row.specific_price is not none else "" }}</td>
      <td>{{ row.integrity }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% endblock %}
"""

_CUSTOMER_TOOLS_TEMPLATE = """
{% extends "base.html" %}
{% block title %}Customer Tools Inventory - ITH{% endblock %}
{% block content %}
<h1>Customer Tools Inventory</h1>
<table>
  <thead>
    <tr><th>Customer</th><th>Serial Number</th><th>Fab Number</th><th>Model</th><th>Unit</th></tr>
  </thead>
  <tbody>
    {% for item in rows %}
    <tr>
      <td>{{ item.customer.customer_name }}</td>
      <td>{{ item.tool.serial_number }}</td>
      <td>{{ item.tool.fab_number or "" }}</td>
      <td>{{ item.tool.model_info or "" }}</td>
      <td>{{ item.unit.name if item.unit else "" }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% endblock %}
"""


_SAP_FINANCIAL_SUMMARY_TEMPLATE = """
{% extends "base.html" %}
{% block title %}SAP Financial Summaries - ITH{% endblock %}
{% block content %}
<h1>SAP Financial Summaries</h1>
{% for document in documents %}
<section>
  <h2>{{ document.title }}</h2>
  {% for summary in document.summaries %}
  <section>
    <h3>{{ summary.title }}</h3>
    <table>
      <thead>
        <tr><th>Group</th><th>Count</th><th>Total</th></tr>
      </thead>
      <tbody>
        {% if summary.rows %}
        {% for row in summary.rows %}
        <tr><td>{{ row.label }}</td><td>{{ row.count }}</td><td>{{ row.total }}</td></tr>
        {% endfor %}
        {% else %}
        <tr><td colspan="3">(none)</td></tr>
        {% endif %}
      </tbody>
    </table>
  </section>
  {% endfor %}
</section>
{% endfor %}
{% endblock %}
"""


_ITEM_USAGE_TEMPLATE = """
{% extends "base.html" %}
{% block title %}Item Usage Analytics - ITH{% endblock %}
{% block content %}
<h1>Item Usage Analytics</h1>
{% for period in periods %}
<section>
  <h2>{{ period.label }}</h2>
  <table>
    <thead>
      <tr>
        <th>Item Code</th>
        <th>Item Name</th>
        <th>Credit Memo Qty</th>
        <th>Invoice Qty</th>
        <th>Production Qty</th>
        <th>Assembly/Disassembly Qty</th>
      </tr>
    </thead>
    <tbody>
      {% if period.rows %}
      {% for row in period.rows %}
      <tr>
        <td>{{ row.item_code }}</td>
        <td>{{ row.item_name }}</td>
        <td>{{ row.credit_memo_qty if row.credit_memo_qty is not none else "" }}</td>
        <td>{{ row.invoice_qty if row.invoice_qty is not none else "" }}</td>
        <td>{{ row.production_qty if row.production_qty is not none else "" }}</td>
        <td>{{ row.assembly_disassembly_qty if row.assembly_disassembly_qty is not none else "" }}</td>
      </tr>
      {% endfor %}
      {% else %}
      <tr><td colspan="6">(none)</td></tr>
      {% endif %}
    </tbody>
  </table>
</section>
{% endfor %}
{% endblock %}
"""


def _financial_summary_document_types(document_type: str | None) -> list[str]:
    selected = (document_type or "").strip().lower()
    if not selected:
        return ["invoice", "credit-memo"]
    return [part.strip().lower() for part in selected.split(",") if part.strip()]


def _financial_summary_group_bys(group_by: str | None) -> list[str]:
    selected = (group_by or "").strip().lower()
    if not selected:
        return ["industry", "item", "salesperson", "state"]
    return [part.strip().lower() for part in selected.split(",") if part.strip()]


def _financial_summary_rows(repository, document_type: str) -> list[object]:
    methods = {
        "invoice": "list_invoice_summaries",
        "credit-memo": "list_credit_memo_summaries",
    }
    method_name = methods.get(document_type)
    if method_name is None:
        raise ValueError(f"Unsupported document type: {document_type}")
    method = getattr(repository, method_name, None)
    if method is None:
        raise RuntimeError(f"Financial summary repository is missing {method_name}()")
    return list(method())


def _financial_summary_label(row, group_by: str) -> str:
    if group_by == "industry":
        return getattr(row, "industry", None) or "Unassigned"
    if group_by == "item":
        item_code = getattr(row, "item_code", None) or ""
        item_name = getattr(row, "item_name", None) or ""
        if item_code and item_name and item_code != item_name:
            return f"{item_code} - {item_name}"
        return item_code or item_name or "Unassigned"
    if group_by == "salesperson":
        return getattr(row, "salesperson", None) or "Unassigned"
    if group_by == "state":
        return getattr(row, "state", None) or "Unassigned"
    raise ValueError(f"Unsupported group by value: {group_by}")


def _financial_summary_group_rows(rows: list[object], group_by: str) -> list[dict[str, str]]:
    grouped: dict[str, list[object]] = defaultdict(list)
    for row in rows:
        grouped[_financial_summary_label(row, group_by)].append(row)
    summary_rows = []
    for label, grouped_rows in sorted(grouped.items(), key=lambda item: item[0].lower()):
        total = Decimal("0")
        for row in grouped_rows:
            total += Decimal(str(getattr(row, "total", 0) or 0))
        summary_rows.append({"label": label, "count": str(len(grouped_rows)), "total": _format_money(total)})
    return summary_rows


def _financial_summary_documents(
    repository, document_types: list[str], group_bys: list[str]
) -> list[dict[str, object]]:
    documents = []
    for document_type in document_types:
        rows = _financial_summary_rows(repository, document_type)
        title = "Invoice Summaries" if document_type == "invoice" else "Credit Memo Summaries"
        summaries = [
            {
                "title": f"By {group_by.replace('-', ' ').title()}",
                "rows": _financial_summary_group_rows(rows, group_by),
            }
            for group_by in group_bys
        ]
        documents.append({"title": title, "summaries": summaries})
    return documents


def _item_usage_period_label(period_years: int) -> str:
    return "1 Year" if period_years == 1 else f"{period_years} Years"


def _item_usage_rows(repository, period_years: int) -> list[object]:
    method = getattr(repository, "list_item_usage", None)
    if method is None:
        raise RuntimeError("Item usage repository is missing list_item_usage()")
    rows = list(method(period_years))
    return sorted(
        rows,
        key=lambda row: (
            (getattr(row, "item_code", None) or "").lower(),
            (getattr(row, "item_name", None) or "").lower(),
        ),
    )


def _item_usage_periods(repository) -> list[dict[str, object]]:
    return [
        {"label": _item_usage_period_label(period_years), "rows": _item_usage_rows(repository, period_years)}
        for period_years in (1, 2, 3)
    ]


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


@bp.route("/packing-list/<int:packing_list_id>")
def packing_list_report(packing_list_id: int):
    session = _get_session()
    try:
        pdf_bytes = build_packing_list_pdf(session, packing_list_id)
        response = Response(pdf_bytes, mimetype="application/pdf")
        response.headers["Content-Disposition"] = (
            f'inline; filename="packing-list-{packing_list_id}.pdf"'
        )
        return response
    finally:
        session.close()


@bp.route("/commercial-invoice-and-sli/<int:packing_list_id>")
def commercial_invoice_and_sli_report(packing_list_id: int):
    session = _get_session()
    try:
        pdf_bytes = build_commercial_invoice_and_sli_pdf(session, packing_list_id)
        response = Response(pdf_bytes, mimetype="application/pdf")
        response.headers["Content-Disposition"] = (
            f'inline; filename="commercial-invoice-and-sli-{packing_list_id}.pdf"'
        )
        return response
    finally:
        session.close()


@bp.route("/check-in/<int:check_in_id>")
def check_in_report(check_in_id: int):
    session = _get_session()
    try:
        pdf_bytes = build_check_in_pdf(session, check_in_id)
        response = Response(pdf_bytes, mimetype="application/pdf")
        response.headers["Content-Disposition"] = (
            f'inline; filename="check-in-{check_in_id}.pdf"'
        )
        return response
    finally:
        session.close()


@bp.route("/ith-test-gauge-certificates/<int:ith_test_gauge_id>")
def ith_test_gauge_certificates_report(ith_test_gauge_id: int):
    session = _get_session()
    try:
        pdf_bytes = build_ith_test_gauge_certificates_pdf(
            session, ith_test_gauge_id, request.args.get("variant")
        )
        response = Response(pdf_bytes, mimetype="application/pdf")
        response.headers["Content-Disposition"] = (
            f'inline; filename="ith-test-gauge-certificates-{ith_test_gauge_id}.pdf"'
        )
        return response
    finally:
        session.close()


@bp.route("/service-measurements/<int:service_id>")
def service_measurements_report(service_id: int):
    session = _get_session()
    try:
        pdf_bytes = build_service_measurements_pdf(session, service_id)
        response = Response(pdf_bytes, mimetype="application/pdf")
        response.headers["Content-Disposition"] = (
            f'inline; filename="service-measurements-{service_id}.pdf"'
        )
        return response
    finally:
        session.close()


@bp.route("/customer-tools/<int:customer_tools_id>")
def customer_tools_report(customer_tools_id: int):
    session = _get_session()
    try:
        pdf_bytes = build_customer_tools_pdf(session, customer_tools_id)
        response = Response(pdf_bytes, mimetype="application/pdf")
        response.headers["Content-Disposition"] = (
            f'inline; filename="customer-tools-{customer_tools_id}.pdf"'
        )
        return response
    finally:
        session.close()


@bp.route("/demo-contract/<int:demo_contract_id>")
def demo_contract_report(demo_contract_id: int):
    session = _get_session()
    try:
        pdf_bytes = build_demo_contract_pdf(session, demo_contract_id)
        response = Response(pdf_bytes, mimetype="application/pdf")
        response.headers["Content-Disposition"] = (
            f'inline; filename="demo-contract-{demo_contract_id}.pdf"'
        )
        return response
    finally:
        session.close()


@bp.route("/field-service/<int:field_service_id>")
def field_service_report(field_service_id: int):
    session = _get_session()
    try:
        pdf_bytes = build_field_service_report_pdf(session, field_service_id)
        response = Response(pdf_bytes, mimetype="application/pdf")
        response.headers["Content-Disposition"] = (
            f'inline; filename="field-service-report-{field_service_id}.pdf"'
        )
        return response
    finally:
        session.close()


@bp.route("/field-service-summary/<int:field_service_id>")
def field_service_summary_report(field_service_id: int):
    session = _get_session()
    try:
        pdf_bytes = build_field_service_summary_pdf(session, field_service_id)
        response = Response(pdf_bytes, mimetype="application/pdf")
        response.headers["Content-Disposition"] = (
            f'inline; filename="field-service-summary-{field_service_id}.pdf"'
        )
        return response
    finally:
        session.close()


@bp.route("/field-service-timesheet/<int:field_service_id>")
def field_service_timesheet_report(field_service_id: int):
    session = _get_session()
    try:
        customer_facing = request.args.get("customer_facing") in {"1", "true", "yes"}
        pdf_bytes = build_field_service_timesheet_pdf(
            session, field_service_id, customer_facing=customer_facing
        )
        response = Response(pdf_bytes, mimetype="application/pdf")
        response.headers["Content-Disposition"] = (
            f'inline; filename="field-service-timesheet-{field_service_id}.pdf"'
        )
        return response
    finally:
        session.close()


@bp.route("/check-in/open-repair-list")
def open_repair_list_report():
    session = _get_session()
    try:
        rows = _open_repair_list_rows(session)
        return render_template_string(_OPEN_REPAIR_LIST_TEMPLATE, rows=rows)
    finally:
        session.close()


@bp.route("/audit-trail")
def audit_trail_report():
    session = _get_session()
    try:
        entity = (request.args.get("entity") or "").strip()
        field = (request.args.get("field") or "").strip()
        rows = _audit_trail_rows(session)
        return render_template_string(
            _AUDIT_TRAIL_TEMPLATE,
            entries=rows,
            entity=entity,
            field=field,
            user=(request.args.get("user") or "").strip(),
            start_date=(request.args.get("start_date") or "").strip(),
            end_date=(request.args.get("end_date") or "").strip(),
        )
    finally:
        session.close()


@bp.route("/shop-data")
def shop_data_report():
    session = _get_session()
    try:
        rows = _shop_data_rows(session)
        return render_template_string(_SHOP_DATA_TEMPLATE, rows=rows)
    finally:
        session.close()


@bp.route("/repair-time-analysis")
def repair_time_analysis_report():
    session = _get_session()
    try:
        rows = _repair_time_analysis_rows(session)
        return render_template_string(_REPAIR_TIME_ANALYSIS_TEMPLATE, rows=rows)
    finally:
        session.close()


@bp.route("/customers/<int:customer_id>")
def customer_detail_report(customer_id: int):
    session = _get_session()
    try:
        context = _customer_detail_context(session, customer_id)
        return render_template_string(_CUSTOMER_DETAIL_TEMPLATE, **context)
    finally:
        session.close()


@bp.route("/customers/by-region")
def customer_by_region_report():
    session = _get_session()
    try:
        groups = _customer_region_groups(session)
        return render_template_string(
            _CUSTOMER_GROUP_TEMPLATE,
            title="Customer Report by Region",
            groups=groups,
        )
    finally:
        session.close()


@bp.route("/customers/by-responsibility")
def customer_by_responsibility_report():
    session = _get_session()
    try:
        groups = _customer_responsibility_groups(session)
        return render_template_string(
            _CUSTOMER_GROUP_TEMPLATE,
            title="Customer Report by Responsibility",
            groups=groups,
        )
    finally:
        session.close()


@bp.route("/customers/pricing")
def customer_pricing_report():
    session = _get_session()
    try:
        customers = _customer_pricing_rows(session)
        return render_template_string(
            _CUSTOMER_PRICING_TEMPLATE,
            customers=customers,
        )
    finally:
        session.close()


@bp.route("/customers/tools-inventory")
def customer_tools_inventory_report():
    session = _get_session()
    try:
        rows = _customer_tools_rows(session)
        return render_template_string(
            _CUSTOMER_TOOLS_TEMPLATE,
            rows=rows,
        )
    finally:
        session.close()


@bp.route("/sap/financial-summaries")
@bp.route("/sap/financial-summaries/<document_type>")
@bp.route("/sap/financial-summaries/<document_type>/<group_by>")
def sap_financial_summaries_report(
    document_type: str | None = None, group_by: str | None = None
):
    repository = current_app.config["SAP_FINANCIAL_SUMMARY_REPOSITORY"]
    documents = _financial_summary_documents(
        repository,
        _financial_summary_document_types(document_type or request.args.get("document_type")),
        _financial_summary_group_bys(group_by or request.args.get("group_by")),
    )
    return render_template_string(_SAP_FINANCIAL_SUMMARY_TEMPLATE, documents=documents)


@bp.route("/sap/item-usage")
def sap_item_usage_report():
    repository = current_app.config["SAP_ITEM_USAGE_REPOSITORY"]
    periods = _item_usage_periods(repository)
    return render_template_string(_ITEM_USAGE_TEMPLATE, periods=periods)
