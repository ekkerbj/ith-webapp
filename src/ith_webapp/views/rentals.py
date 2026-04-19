from flask import Blueprint, current_app, redirect, render_template, request, url_for

from ith_webapp.models.rental import Rental

bp = Blueprint("rentals", __name__, url_prefix="/rentals")


def _get_session():
    factory = current_app.config["SESSION_FACTORY"]
    return factory()


@bp.route("/")
def rental_list():
    session = _get_session()
    try:
        items = session.query(Rental).order_by(Rental.rental_id).all()
        return render_template("rentals/list.html", items=items)
    finally:
        session.close()


@bp.route("/<int:rental_id>")
def rental_detail(rental_id: int):
    session = _get_session()
    try:
        item = session.get(Rental, rental_id)
        if item is None:
            return "Not found", 404
        return render_template("rentals/detail.html", item=item)
    finally:
        session.close()


@bp.route("/new", methods=["GET", "POST"])
def rental_create():
    if request.method == "GET":
        return render_template("rentals/form.html")

    session = _get_session()
    try:
        item = Rental(
            customer_id=int(request.form.get("customer_id") or 0),
            customer_tools_id=int(request.form.get("customer_tools_id") or 0),
            rental_status_id=int(request.form.get("rental_status_id") or 0),
        )
        session.add(item)
        session.commit()
        return redirect(url_for("rentals.rental_detail", rental_id=item.rental_id))
    finally:
        session.close()


@bp.route("/<int:rental_id>/edit", methods=["GET", "POST"])
def rental_edit(rental_id: int):
    session = _get_session()
    try:
        item = session.get(Rental, rental_id)
        if item is None:
            return "Not found", 404
        if request.method == "GET":
            return render_template("rentals/form.html", item=item)
        item.customer_id = int(request.form.get("customer_id") or 0)
        item.customer_tools_id = int(request.form.get("customer_tools_id") or 0)
        item.rental_status_id = int(request.form.get("rental_status_id") or 0)
        session.commit()
        return redirect(url_for("rentals.rental_detail", rental_id=rental_id))
    finally:
        session.close()


@bp.route("/<int:rental_id>/delete", methods=["POST"])
def rental_delete(rental_id: int):
    session = _get_session()
    try:
        item = session.get(Rental, rental_id)
        if item is None:
            return "Not found", 404
        session.delete(item)
        session.commit()
        return redirect(url_for("rentals.rental_list"))
    finally:
        session.close()
