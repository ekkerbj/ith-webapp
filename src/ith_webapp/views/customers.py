from flask import Blueprint, current_app, redirect, render_template, request, url_for

from ith_webapp.models.customer import Customer
from ith_webapp.repositories.customer_repository import CustomerRepository

bp = Blueprint("customers", __name__, url_prefix="/customers")


def _get_session():
    factory = current_app.config["SESSION_FACTORY"]
    return factory()


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
        if request.method == "GET":
            return render_template("customers/form.html", customer=customer)
        customer.customer_name = request.form.get("customer_name")
        customer.card_code = request.form.get("card_code")
        customer.active = request.form.get("active") == "on"
        customer.website = request.form.get("website") or None
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
        session.delete(customer)
        session.commit()
        return redirect(url_for("customers.customer_list"))
    finally:
        session.close()
