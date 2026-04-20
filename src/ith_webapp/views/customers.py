from flask import Blueprint, current_app, redirect, render_template, request, url_for

from ith_webapp.models.customer import Customer
from ith_webapp.repositories.customer_repository import CustomerRepository
from ith_webapp.services.audit_trail import record_audit_change

bp = Blueprint("customers", __name__, url_prefix="/customers")

CUSTOMER_AUDIT_FIELDS = ("customer_name", "card_code", "active", "website")


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


@bp.route("/new", methods=["GET", "POST"])
def customer_create():
    if request.method == "GET":
        return render_template("customers/form.html")
    session = _get_session()
    try:
        repo = CustomerRepository(session)
        customer = Customer(
            customer_name=request.form.get("customer_name"),
            card_code=request.form.get("card_code"),
            active=request.form.get("active") == "on",
            website=request.form.get("website") or None,
        )
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
        repo = CustomerRepository(session)
        customers = repo.find_all()
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
        customer.customer_name = request.form.get("customer_name")
        customer.card_code = request.form.get("card_code")
        customer.active = request.form.get("active") == "on"
        customer.website = request.form.get("website") or None
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
