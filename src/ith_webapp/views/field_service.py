from sqlalchemy import or_

from flask import Blueprint, current_app, redirect, render_template, request, url_for

from ith_webapp.models.customer import Customer
from ith_webapp.models.field_service import FieldService
from ith_webapp.models.field_service_status import FieldServiceStatus
from ith_webapp.services.date_filtering import current_month_filter
from ith_webapp.services.list_exports import build_list_export_response
from ith_webapp.services.pagination import paginate_query
from ith_webapp.services.table_sorting import apply_sorting, build_sortable_columns
from ith_webapp.views.session import get_session

bp = Blueprint("field_services", __name__, url_prefix="/field-services")


def _get_session():
    return get_session()


@bp.route("/")
def field_service_list():
    session = _get_session()
    try:
        items_query = (
            session.query(FieldService)
            .join(FieldService.customer)
            .join(FieldService.field_service_status)
            .filter(current_month_filter(FieldService.visit_date))
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
        items_query, current_sort, current_direction = apply_sorting(
            items_query,
            request.args,
            {
                "customer_name": Customer.customer_name,
                "status": FieldServiceStatus.name,
                "notes": FieldService.visit_notes,
                "field_service_id": FieldService.field_service_id,
            },
            "field_service_id",
        )
        headers = [
            "Customer",
            "Status",
            "Notes",
        ]
        export_rows = [
            [
                getattr(item.customer, "customer_name", "") or "",
                getattr(item.field_service_status, "name", "") or "",
                item.visit_notes or "",
            ]
            for item in items_query.all()
        ]
        export_response = build_list_export_response(
            title="Field Services",
            headers=headers,
            rows=export_rows,
            export_format=request.args.get("format"),
        )
        if export_response is not None:
            return export_response
        items, pagination = paginate_query(
            items_query,
            "field_services.field_service_list",
            request.args,
            request.args.get("page", 1, type=int),
            request.args.get(
                "page_size",
                current_app.config["LIST_PAGE_SIZE"],
                type=int,
            ),
        )
        columns = build_sortable_columns(
            "field_services.field_service_list",
            request.args,
            (
                ("Customer", "customer_name"),
                ("Status", "status"),
                ("Notes", "notes"),
            ),
            current_sort,
            current_direction,
        )
        rows = [
            {
                "url": url_for("field_services.field_service_detail", field_service_id=item.field_service_id),
                "values": [
                    getattr(item.customer, "customer_name", "") or "",
                    getattr(item.field_service_status, "name", "") or "",
                    item.visit_notes or "",
                ],
            }
            for item in items
        ]
        return render_template(
            "crud/list.html",
            title="Field Services",
            heading="Field service queue",
            hero_text="Open the active service visits for this month.",
            primary_action_url=url_for("field_services.field_service_create"),
            primary_action_label="Create field service",
            columns=columns,
            rows=rows,
            pagination=pagination,
            empty_message="No field services found.",
        )
    finally:
        session.close()


@bp.route("/<int:field_service_id>")
def field_service_detail(field_service_id: int):
    session = _get_session()
    try:
        item = session.get(FieldService, field_service_id)
        if item is None:
            return "Not found", 404
        return render_template(
            "field_services/detail.html",
            item=item,
            back_url=url_for("field_services.field_service_list"),
            edit_label="Edit service",
        )
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
