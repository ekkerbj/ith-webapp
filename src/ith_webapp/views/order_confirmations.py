from flask import Blueprint, current_app, redirect, render_template, request, url_for

from ith_webapp.models.order_confirmation import OrderConfirmation

bp = Blueprint("order_confirmations", __name__, url_prefix="/order-confirmations")


def _get_session():
    factory = current_app.config["SESSION_FACTORY"]
    return factory()


@bp.route("/")
def order_confirmation_list():
    session = _get_session()
    try:
        items = (
            session.query(OrderConfirmation)
            .order_by(OrderConfirmation.order_confirmation_id)
            .all()
        )
        return render_template("order_confirmations/list.html", items=items)
    finally:
        session.close()


@bp.route("/<int:order_confirmation_id>")
def order_confirmation_detail(order_confirmation_id: int):
    session = _get_session()
    try:
        item = session.get(OrderConfirmation, order_confirmation_id)
        if item is None:
            return "Not found", 404
        return render_template("order_confirmations/detail.html", item=item)
    finally:
        session.close()


@bp.route("/new", methods=["GET", "POST"])
def order_confirmation_create():
    if request.method == "GET":
        return render_template("order_confirmations/form.html")

    session = _get_session()
    try:
        item = OrderConfirmation(
            customer_id=int(request.form.get("customer_id") or 0),
            order_number=request.form.get("order_number") or None,
            notes=request.form.get("notes") or None,
        )
        session.add(item)
        session.commit()
        return redirect(
            url_for(
                "order_confirmations.order_confirmation_detail",
                order_confirmation_id=item.order_confirmation_id,
            )
        )
    finally:
        session.close()


@bp.route("/<int:order_confirmation_id>/edit", methods=["GET", "POST"])
def order_confirmation_edit(order_confirmation_id: int):
    session = _get_session()
    try:
        item = session.get(OrderConfirmation, order_confirmation_id)
        if item is None:
            return "Not found", 404
        if request.method == "GET":
            return render_template("order_confirmations/form.html", item=item)
        item.customer_id = int(request.form.get("customer_id") or 0)
        item.order_number = request.form.get("order_number") or None
        item.notes = request.form.get("notes") or None
        session.commit()
        return redirect(
            url_for(
                "order_confirmations.order_confirmation_detail",
                order_confirmation_id=order_confirmation_id,
            )
        )
    finally:
        session.close()


@bp.route("/<int:order_confirmation_id>/delete", methods=["POST"])
def order_confirmation_delete(order_confirmation_id: int):
    session = _get_session()
    try:
        item = session.get(OrderConfirmation, order_confirmation_id)
        if item is None:
            return "Not found", 404
        session.delete(item)
        session.commit()
        return redirect(url_for("order_confirmations.order_confirmation_list"))
    finally:
        session.close()
