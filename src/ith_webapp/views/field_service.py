from sqlalchemy import or_

from flask import Blueprint, current_app, redirect, render_template, request, url_for

from ith_webapp.models.customer import Customer
from ith_webapp.models.field_service import FieldService
from ith_webapp.models.field_service_status import FieldServiceStatus

bp = Blueprint("field_services", __name__, url_prefix="/field-services")


def _get_session():
    factory = current_app.config["SESSION_FACTORY"]
    return factory()


@bp.route("/")
def field_service_list():
    session = _get_session()
    try:
        items_query = (
            session.query(FieldService)
            .join(FieldService.customer)
            .join(FieldService.field_service_status)
        )
        query = (request.args.get("q") or "").strip()
        if query:
            like = f"%{query}%"
            conditions = [
                FieldServiceStatus.name.ilike(like),
                Customer.customer_name.ilike(like),
            ]
            if query.isdigit():
                conditions.append(FieldService.field_service_id == int(query))
            items_query = items_query.filter(or_(*conditions))
        items = items_query.order_by(FieldService.field_service_id).all()
        return render_template("field_services/list.html", items=items)
    finally:
        session.close()


@bp.route("/<int:field_service_id>")
def field_service_detail(field_service_id: int):
    session = _get_session()
    try:
        item = session.get(FieldService, field_service_id)
        if item is None:
            return "Not found", 404
        return render_template("field_services/detail.html", item=item)
    finally:
        session.close()


@bp.route("/new", methods=["GET", "POST"])
def field_service_create():
    if request.method == "GET":
        return render_template("field_services/form.html")

    session = _get_session()
    try:
        item = FieldService(
            customer_id=int(request.form.get("customer_id") or 0),
            field_service_status_id=int(request.form.get("field_service_status_id") or 0),
            visit_notes=request.form.get("visit_notes") or None,
        )
        session.add(item)
        session.commit()
        return redirect(
            url_for(
                "field_services.field_service_detail",
                field_service_id=item.field_service_id,
            )
        )
    finally:
        session.close()


@bp.route("/<int:field_service_id>/edit", methods=["GET", "POST"])
def field_service_edit(field_service_id: int):
    session = _get_session()
    try:
        item = session.get(FieldService, field_service_id)
        if item is None:
            return "Not found", 404
        if request.method == "GET":
            return render_template("field_services/form.html", item=item)
        item.customer_id = int(request.form.get("customer_id") or 0)
        item.field_service_status_id = int(
            request.form.get("field_service_status_id") or 0
        )
        item.visit_notes = request.form.get("visit_notes") or None
        session.commit()
        return redirect(
            url_for(
                "field_services.field_service_detail",
                field_service_id=field_service_id,
            )
        )
    finally:
        session.close()


@bp.route("/<int:field_service_id>/delete", methods=["POST"])
def field_service_delete(field_service_id: int):
    session = _get_session()
    try:
        item = session.get(FieldService, field_service_id)
        if item is None:
            return "Not found", 404
        session.delete(item)
        session.commit()
        return redirect(url_for("field_services.field_service_list"))
    finally:
        session.close()
