from decimal import Decimal, InvalidOperation

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    render_template_string,
    request,
    session,
    url_for,
)
from sqlalchemy import or_

from ith_webapp.models.customer import Customer
from ith_webapp.models.customer_address import CustomerAddress
from ith_webapp.repositories.customer_repository import CustomerRepository
from ith_webapp.services.list_exports import build_list_export_response
from ith_webapp.services.pagination import paginate_query
from ith_webapp.services.table_sorting import apply_sorting, build_sortable_columns
from ith_webapp.services.audit_trail import record_audit_change
from ith_webapp.views.session import get_session

bp = Blueprint("customers", __name__, url_prefix="/customers")

CUSTOMER_FIELD_LIMITS = {
    "customer_name": ("Customer Name", 100),
    "card_code": ("Card Code", 75),
    "website": ("Website", 50),
    "salesperson": ("Sales Rep", 100),
    "territory": ("Territory", 100),
    "credit_limit": ("Credit Limit", None),
    "tax_group": ("Tax Group", 50),
    "tax_exempt_number": ("Tax Exempt Number", 50),
    "contact_name": ("Contact Name", 100),
    "phone": ("Phone", 50),
    "fax": ("Fax", 50),
    "email": ("Email", 100),
    "plant_name": ("Plant Name", 100),
    "site_name": ("Site Name", 100),
    "site_address": ("Site Address", 100),
    "site_city": ("Site City", 100),
    "site_state": ("Site State", 50),
    "site_zip_code": ("Site Zip Code", 20),
    "site_country": ("Site Country", 50),
    "ship_via": ("Ship Via", 50),
    "freight_terms": ("Freight Terms", 100),
    "shipping_instructions": ("Shipping Instructions", None),
    "billing_instructions": ("Billing Instructions", None),
    "comments": ("Comments", None),
    "repair_instructions": ("Repair Instructions", None),
    "multiplier": ("Multiplier", None),
    "lead_id": ("Lead ID", None),
    "responsibility_id": ("Responsibility ID", None),
    "calibration_interval": ("Calibration Interval", None),
}
CUSTOMER_INT_FIELDS = {
    "price_list_num": "Price List Num",
    "lead_id": "Lead ID",
    "responsibility_id": "Responsibility ID",
    "calibration_interval": "Calibration Interval",
}
CUSTOMER_DECIMAL_FIELDS = {
    "credit_limit": "Credit Limit",
    "multiplier": "Multiplier",
}
CUSTOMER_TEXTAREA_FIELDS = {
    "shipping_instructions",
    "billing_instructions",
    "comments",
    "repair_instructions",
}

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
    return get_session()


def _current_user_email() -> str | None:
    firebase_user = session.get("firebase_user")
    if isinstance(firebase_user, dict):
        email = firebase_user.get("email")
        if isinstance(email, str) and email:
            return email
    return None


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


def _customer_form_values(customer: Customer | None = None) -> dict[str, object]:
    if customer is None:
        return {
            "customer_name": "",
            "card_code": "",
            "active": False,
            "website": "",
            "price_list_num": "",
            "salesperson": "",
            "territory": "",
            "credit_limit": "",
            "tax_group": "",
            "tax_exempt_number": "",
            "contact_name": "",
            "phone": "",
            "fax": "",
            "email": "",
            "plant_name": "",
            "site_name": "",
            "site_address": "",
            "site_city": "",
            "site_state": "",
            "site_zip_code": "",
            "site_country": "",
            "ship_via": "",
            "freight_terms": "",
            "shipping_instructions": "",
            "billing_instructions": "",
            "comments": "",
            "repair_instructions": "",
            "multiplier": "",
            "lead_id": "",
            "responsibility_id": "",
            "calibration_interval": "",
        }
    return {
        "customer_name": customer.customer_name or "",
        "card_code": customer.card_code or "",
        "active": customer.active,
        "website": customer.website or "",
        "price_list_num": "" if customer.price_list_num is None else customer.price_list_num,
        "salesperson": customer.salesperson or "",
        "territory": customer.territory or "",
        "credit_limit": "" if customer.credit_limit is None else customer.credit_limit,
        "tax_group": customer.tax_group or "",
        "tax_exempt_number": customer.tax_exempt_number or "",
        "contact_name": customer.contact_name or "",
        "phone": customer.phone or "",
        "fax": customer.fax or "",
        "email": customer.email or "",
        "plant_name": customer.plant_name or "",
        "site_name": customer.site_name or "",
        "site_address": customer.site_address or "",
        "site_city": customer.site_city or "",
        "site_state": customer.site_state or "",
        "site_zip_code": customer.site_zip_code or "",
        "site_country": customer.site_country or "",
        "ship_via": customer.ship_via or "",
        "freight_terms": customer.freight_terms or "",
        "shipping_instructions": customer.shipping_instructions or "",
        "billing_instructions": customer.billing_instructions or "",
        "comments": customer.comments or "",
        "repair_instructions": customer.repair_instructions or "",
        "multiplier": "" if customer.multiplier is None else customer.multiplier,
        "lead_id": "" if customer.lead_id is None else customer.lead_id,
        "responsibility_id": "" if customer.responsibility_id is None else customer.responsibility_id,
        "calibration_interval": "" if customer.calibration_interval is None else customer.calibration_interval,
    }


def _posted_customer_form_values() -> dict[str, object]:
    form = request.form
    return {
        "customer_name": form.get("customer_name", "").strip(),
        "card_code": form.get("card_code", "").strip(),
        "active": form.get("active") == "on",
        "website": form.get("website", "").strip(),
        "price_list_num": form.get("price_list_num", "").strip(),
        "salesperson": (form.get("salesperson") or form.get("sales_rep") or "").strip(),
        "territory": form.get("territory", "").strip(),
        "credit_limit": form.get("credit_limit", "").strip(),
        "tax_group": form.get("tax_group", "").strip(),
        "tax_exempt_number": form.get("tax_exempt_number", "").strip(),
        "contact_name": form.get("contact_name", "").strip(),
        "phone": form.get("phone", "").strip(),
        "fax": form.get("fax", "").strip(),
        "email": form.get("email", "").strip(),
        "plant_name": form.get("plant_name", "").strip(),
        "site_name": form.get("site_name", "").strip(),
        "site_address": form.get("site_address", "").strip(),
        "site_city": form.get("site_city", "").strip(),
        "site_state": form.get("site_state", "").strip(),
        "site_zip_code": form.get("site_zip_code", "").strip(),
        "site_country": form.get("site_country", "").strip(),
        "ship_via": form.get("ship_via", "").strip(),
        "freight_terms": form.get("freight_terms", "").strip(),
        "shipping_instructions": form.get("shipping_instructions", "").strip(),
        "billing_instructions": form.get("billing_instructions", "").strip(),
        "comments": form.get("comments", "").strip(),
        "repair_instructions": form.get("repair_instructions", "").strip(),
        "multiplier": form.get("multiplier", "").strip(),
        "lead_id": form.get("lead_id", "").strip(),
        "responsibility_id": form.get("responsibility_id", "").strip(),
        "calibration_interval": form.get("calibration_interval", "").strip(),
    }


def _validate_customer_form() -> tuple[dict[str, object | None], dict[str, list[str]]]:
    form_values = _posted_customer_form_values()
    errors: dict[str, list[str]] = {}
    data: dict[str, object | None] = {
        "active": form_values["active"],
        "shipping_instructions": form_values["shipping_instructions"] or None,
        "billing_instructions": form_values["billing_instructions"] or None,
        "comments": form_values["comments"] or None,
        "repair_instructions": form_values["repair_instructions"] or None,
    }

    for field, (label, max_length) in CUSTOMER_FIELD_LIMITS.items():
        if field in CUSTOMER_INT_FIELDS or field in CUSTOMER_DECIMAL_FIELDS:
            continue
        if field in CUSTOMER_TEXTAREA_FIELDS:
            continue
        value = form_values[field]
        if field == "customer_name" and not value:
            errors.setdefault(field, []).append(f"{label} is required.")
        elif value and max_length is not None and len(value) > max_length:
            errors.setdefault(field, []).append(
                f"{label} must be {max_length} characters or fewer."
            )
        data[field] = value or None

    for field, label in CUSTOMER_INT_FIELDS.items():
        value = form_values[field]
        if not value:
            data[field] = None
            continue
        try:
            data[field] = int(value)
        except ValueError:
            errors.setdefault(field, []).append(f"{label} must be a whole number.")

    for field, label in CUSTOMER_DECIMAL_FIELDS.items():
        value = form_values[field]
        if not value:
            data[field] = None
            continue
        try:
            data[field] = Decimal(value)
        except InvalidOperation:
            errors.setdefault(field, []).append(f"{label} must be a decimal number.")

    return data, errors


def _has_customer_form_errors(errors: dict[str, list[str]]) -> bool:
    return any(errors.values())


def _render_customer_form(
    *,
    customer: Customer | None = None,
    form_values: dict[str, object] | None = None,
    errors: dict[str, list[str]] | None = None,
) -> str:
    return render_template(
        "customers/form.html",
        customer=customer,
        form=form_values or _customer_form_values(customer),
        errors=errors or {},
    )


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
        return _render_customer_form()
    session = _get_session()
    try:
        repo = CustomerRepository(session)
        form_values = _posted_customer_form_values()
        customer_data, errors = _validate_customer_form()
        if _has_customer_form_errors(errors):
            flash("Please correct the highlighted errors and try again.", "error")
            return _render_customer_form(form_values=form_values, errors=errors)
        customer = Customer(**customer_data)
        repo.save(customer)
        session.flush()
        record_audit_change(
            session,
            table_name="customer",
            record_id=customer.customer_id,
            action="create",
            changes={field: (None, value) for field, value in _customer_snapshot(customer).items()},
            changed_by=_current_user_email(),
        )
        session.commit()
        flash("Customer created successfully.", "success")
        return redirect(url_for("customers.customer_list"))
    finally:
        session.close()


@bp.route("/")
def customer_list():
    session = _get_session()
    try:
        query = (request.args.get("q") or "").strip()
        items_query = session.query(Customer)
        if query:
            like = f"%{query}%"
            items_query = items_query.filter(
                or_(
                    Customer.customer_name.ilike(like),
                    Customer.card_code.ilike(like),
                )
            )
        items_query, current_sort, current_direction = apply_sorting(
            items_query,
            request.args,
            {
                "customer_name": Customer.customer_name,
                "card_code": Customer.card_code,
                "active": Customer.active,
                "customer_id": Customer.customer_id,
            },
            "customer_id",
        )
        headers = [
            "Name",
            "Card Code",
            "Active",
        ]
        export_rows = [
            [
                item.customer_name or "",
                item.card_code or "",
                "Yes" if item.active else "No",
            ]
            for item in items_query.all()
        ]
        export_response = build_list_export_response(
            title="Customers",
            headers=headers,
            rows=export_rows,
            export_format=request.args.get("format"),
        )
        if export_response is not None:
            return export_response
        items, pagination = paginate_query(
            items_query,
            "customers.customer_list",
            request.args,
            request.args.get("page", 1, type=int),
            request.args.get(
                "page_size",
                current_app.config["LIST_PAGE_SIZE"],
                type=int,
            ),
        )
        columns = build_sortable_columns(
            "customers.customer_list",
            request.args,
            (
                ("Name", "customer_name"),
                ("Card Code", "card_code"),
                ("Active", "active"),
            ),
            current_sort,
            current_direction,
        )
        rows = [
            {
                "url": url_for("customers.customer_detail", customer_id=item.customer_id),
                "values": [
                    item.customer_name or "",
                    item.card_code or "",
                    "Yes" if item.active else "No",
                ],
            }
            for item in items
        ]
        return render_template(
            "crud/list.html",
            title="Customers",
            heading="Customers",
            columns=columns,
            rows=rows,
            pagination=pagination,
            empty_message="No customers found.",
        )
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
            return _render_customer_form(customer=customer)
        form_values = _posted_customer_form_values()
        customer_data, errors = _validate_customer_form()
        if _has_customer_form_errors(errors):
            flash("Please correct the highlighted errors and try again.", "error")
            return _render_customer_form(
                customer=customer,
                form_values=form_values,
                errors=errors,
            )
        for field, value in customer_data.items():
            setattr(customer, field, value)
        record_audit_change(
            session,
            table_name="customer",
            record_id=customer.customer_id,
            action="edit",
            changes=_customer_changes(before, _customer_snapshot(customer)),
            changed_by=_current_user_email(),
        )
        session.commit()
        flash("Customer updated successfully.", "success")
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
            changed_by=_current_user_email(),
        )
        session.commit()
        flash("Customer deleted successfully.", "success")
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
