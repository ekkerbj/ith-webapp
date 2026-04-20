from decimal import Decimal

from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    render_template_string,
    request,
    url_for,
)
from sqlalchemy import select

from ith_webapp.models.customer import Customer
from ith_webapp.models.customer_address import CustomerAddress
from ith_webapp.repositories.customer_repository import CustomerRepository
from ith_webapp.services.audit_trail import record_audit_change

bp = Blueprint("customers", __name__, url_prefix="/customers")

CUSTOMER_AUDIT_FIELDS = (
    "customer_name",
    "card_code",
    "active",
    "website",
    "price_list_num",
    "salesperson",
    "territory",
    "credit_limit",
    "tax_group",
    "tax_exempt_number",
    "contact_name",
    "phone",
    "fax",
    "email",
    "plant_name",
    "site_name",
    "site_address",
    "site_city",
    "site_state",
    "site_zip_code",
    "site_country",
    "ship_via",
    "freight_terms",
    "shipping_instructions",
    "billing_instructions",
    "comments",
    "repair_instructions",
    "multiplier",
    "lead_id",
    "responsibility_id",
    "calibration_interval",
)


def _get_session():
    factory = current_app.config["SESSION_FACTORY"]
    return factory()


def _customer_snapshot(customer: Customer) -> dict[str, object | None]:
    return {field: getattr(customer, field) for field in CUSTOMER_AUDIT_FIELDS}


def _customer_changes(
    before: dict[str, object | None],
    after: dict[str, object | None],
) -> dict[str, tuple[object | None, object | None]]:
    return {
        field: (before[field], after[field])
        for field in CUSTOMER_AUDIT_FIELDS
        if before[field] != after[field]
    }


def _form_int(name: str) -> int | None:
    value = request.form.get(name)
    return int(value) if value else None


def _form_decimal(name: str) -> Decimal | None:
    value = request.form.get(name)
    return Decimal(value) if value else None


def _customer_form_data() -> dict[str, object | None]:
    return {
        "customer_name": request.form.get("customer_name") or None,
        "card_code": request.form.get("card_code") or None,
        "active": request.form.get("active") == "on",
        "website": request.form.get("website") or None,
        "price_list_num": _form_int("price_list_num"),
        "salesperson": (
            request.form.get("salesperson")
            or request.form.get("sales_rep")
            or None
        ),
        "territory": request.form.get("territory") or None,
        "credit_limit": _form_decimal("credit_limit"),
        "tax_group": request.form.get("tax_group") or None,
        "tax_exempt_number": request.form.get("tax_exempt_number") or None,
        "contact_name": request.form.get("contact_name") or None,
        "phone": request.form.get("phone") or None,
        "fax": request.form.get("fax") or None,
        "email": request.form.get("email") or None,
        "plant_name": request.form.get("plant_name") or None,
        "site_name": request.form.get("site_name") or None,
        "site_address": request.form.get("site_address") or None,
        "site_city": request.form.get("site_city") or None,
        "site_state": request.form.get("site_state") or None,
        "site_zip_code": request.form.get("site_zip_code") or None,
        "site_country": request.form.get("site_country") or None,
        "ship_via": request.form.get("ship_via") or None,
        "freight_terms": request.form.get("freight_terms") or None,
        "shipping_instructions": request.form.get("shipping_instructions") or None,
        "billing_instructions": request.form.get("billing_instructions") or None,
        "comments": request.form.get("comments") or None,
        "repair_instructions": request.form.get("repair_instructions") or None,
        "multiplier": _form_decimal("multiplier"),
        "lead_id": _form_int("lead_id"),
        "responsibility_id": _form_int("responsibility_id"),
        "calibration_interval": _form_int("calibration_interval"),
    }


def _customer_addresses(session, customer_id: int) -> list[CustomerAddress]:
    return (
        session.query(CustomerAddress)
        .filter(CustomerAddress.customer_id == customer_id)
        .order_by(CustomerAddress.address_id)
        .all()
    )


def _primary_customer_address(session, customer_id: int) -> CustomerAddress | None:
    addresses = _customer_addresses(session, customer_id)
    return addresses[0] if addresses else None


def _customer_label_lines(
    customer: Customer,
    address: CustomerAddress | None,
    variant: str,
) -> list[str]:
    lines = [customer.customer_name or ""]
    if customer.card_code:
        lines.append(f"Card Code: {customer.card_code}")
    if variant == "mailing" and address is not None:
        lines.extend(
            [
                address.street,
                f"{address.city}, {address.state} {address.zip_code}",
                address.country,
            ]
        )
    elif address is not None:
        lines.append(address.address_type)
        lines.extend(
            [
                address.street,
                f"{address.city}, {address.state} {address.zip_code}",
                address.country,
            ]
        )
    if variant == "sap":
        lines.insert(0, "SAP Address Label")
    return lines


def _render_customer_labels(title: str, variant: str, layout: str) -> str:
    session = _get_session()
    try:
        customers = (
            session.query(Customer)
            .order_by(Customer.customer_id)
            .all()
        )
        labels = [
            {
                "customer_id": customer.customer_id,
                "lines": _customer_label_lines(
                    customer,
                    _primary_customer_address(session, customer.customer_id),
                    variant,
                ),
            }
            for customer in customers
        ]
        return render_template_string(
            """
            {% extends "base.html" %}
            {% block title %}{{ title }} - ITH{% endblock %}
            {% block content %}
            <h1>{{ title }}</h1>
            <section class="customer-label-sheet customer-label-sheet--{{ layout }}">
              {% if labels %}
                {% for label in labels %}
                <article class="customer-label">
                  {% for line in label.lines %}
                  <div>{{ line }}</div>
                  {% endfor %}
                </article>
                {% endfor %}
              {% else %}
                <p>No customers found.</p>
              {% endif %}
            </section>
            {% endblock %}
            """,
            title=title,
            labels=labels,
            layout=layout,
        )
    finally:
        session.close()


@bp.route("/new", methods=["GET", "POST"])
def customer_create():
    if request.method == "GET":
        return render_template("customers/form.html")
    session = _get_session()
    try:
        repo = CustomerRepository(session)
        customer = Customer(**_customer_form_data())
        repo.save(customer)
        session.flush()
        record_audit_change(
            session,
            table_name="customer",
            record_id=customer.customer_id,
            action="create",
            changes={field: (None, value) for field, value in _customer_snapshot(customer).items()},
        )
        session.commit()
        return redirect(url_for("customers.customer_list"))
    finally:
        session.close()


@bp.route("/")
def customer_list():
    session = _get_session()
    try:
        query = (request.args.get("q") or "").strip()
        stmt = select(Customer).order_by(Customer.customer_id)
        if query:
            like = f"%{query}%"
            stmt = stmt.where(
                Customer.customer_name.ilike(like) | Customer.card_code.ilike(like)
            )
        customers = list(session.scalars(stmt).all())
        return render_template("customers/list.html", customers=customers)
    finally:
        session.close()


@bp.route("/<int:customer_id>")
def customer_detail(customer_id: int):
    session = _get_session()
    try:
        repo = CustomerRepository(session)
        customer = repo.find_by_id(customer_id)
        if customer is None:
            return "Not found", 404
        return render_template("customers/detail.html", customer=customer)
    finally:
        session.close()


@bp.route("/<int:customer_id>/edit", methods=["GET", "POST"])
def customer_edit(customer_id: int):
    session = _get_session()
    try:
        repo = CustomerRepository(session)
        customer = repo.find_by_id(customer_id)
        if customer is None:
            return "Not found", 404
        before = _customer_snapshot(customer)
        if request.method == "GET":
            return render_template("customers/form.html", customer=customer)
        for field, value in _customer_form_data().items():
            setattr(customer, field, value)
        record_audit_change(
            session,
            table_name="customer",
            record_id=customer.customer_id,
            action="edit",
            changes=_customer_changes(before, _customer_snapshot(customer)),
        )
        session.commit()
        return redirect(url_for("customers.customer_detail", customer_id=customer_id))
    finally:
        session.close()


@bp.route("/<int:customer_id>/delete", methods=["POST"])
def customer_delete(customer_id: int):
    session = _get_session()
    try:
        repo = CustomerRepository(session)
        customer = repo.find_by_id(customer_id)
        if customer is None:
            return "Not found", 404
        before = _customer_snapshot(customer)
        session.delete(customer)
        record_audit_change(
            session,
            table_name="customer",
            record_id=customer_id,
            action="delete",
            changes={field: (value, None) for field, value in before.items()},
        )
        session.commit()
        return redirect(url_for("customers.customer_list"))
    finally:
        session.close()


@bp.route("/labels/<variant>")
def customer_labels(variant: str):
    titles = {
        "mailing": "Mailing Labels",
        "address": "Address Labels",
        "sap": "SAP Address Labels",
    }
    if variant not in titles:
        return "Not found", 404
    layout = request.args.get("format", "single").lower()
    if layout not in {"single", "multi"}:
        layout = "single"
    return _render_customer_labels(titles[variant], variant, layout)
