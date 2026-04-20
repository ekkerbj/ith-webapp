from flask import Blueprint, current_app, redirect, render_template, request, url_for

from ith_webapp.models.customer import Customer
from ith_webapp.models.consignment_list import ConsignmentList
from ith_webapp.models.part import Part
from ith_webapp.services.pagination import paginate_query
from ith_webapp.services.table_sorting import apply_sorting, build_sortable_columns
from ith_webapp.views.session import get_session

bp = Blueprint("consignment_list", __name__, url_prefix="/consignment-lists")


def _get_session():
    return get_session()


@bp.route("/")
def consignment_list():
    session = _get_session()
    try:
        items_query = (
            session.query(ConsignmentList)
            .join(ConsignmentList.customer)
            .join(ConsignmentList.part)
        )
        items_query, current_sort, current_direction = apply_sorting(
            items_query,
            request.args,
            {
                "customer_name": Customer.customer_name,
                "part_number": Part.part_number,
                "quantity": ConsignmentList.quantity,
                "consignment_list_id": ConsignmentList.consignment_list_id,
            },
            "consignment_list_id",
        )
        items, pagination = paginate_query(
            items_query,
            "consignment_list.consignment_list",
            request.args,
            request.args.get("page", 1, type=int),
            request.args.get(
                "page_size",
                current_app.config["LIST_PAGE_SIZE"],
                type=int,
            ),
        )
        columns = build_sortable_columns(
            "consignment_list.consignment_list",
            request.args,
            (
                ("Customer", "customer_name"),
                ("Part", "part_number"),
                ("Quantity", "quantity"),
            ),
            current_sort,
            current_direction,
        )
        rows = [
            {
                "url": url_for(
                    "consignment_list.consignment_list_detail",
                    consignment_list_id=item.consignment_list_id,
                ),
                "values": [
                    getattr(item.customer, "customer_name", "") or "",
                    getattr(item.part, "part_number", "") or "",
                    item.quantity,
                ],
            }
            for item in items
        ]
        return render_template(
            "crud/list.html",
            title="Consignment Lists",
            heading="Consignment Lists",
            columns=columns,
            rows=rows,
            pagination=pagination,
            empty_message="No consignment items found.",
        )
    finally:
        session.close()


@bp.route("/<int:consignment_list_id>")
def consignment_list_detail(consignment_list_id: int):
    session = _get_session()
    try:
        item = session.get(ConsignmentList, consignment_list_id)
        if item is None:
            return "Not found", 404
        return render_template("consignment_list/detail.html", item=item)
    finally:
        session.close()


@bp.route("/new", methods=["GET", "POST"])
def consignment_list_create():
    if request.method == "GET":
        return render_template("consignment_list/form.html")

    session = _get_session()
    try:
        item = ConsignmentList(
            customer_id=int(request.form.get("customer_id") or 0),
            part_id=int(request.form.get("part_id") or 0),
            quantity=int(request.form.get("quantity") or 0),
        )
        session.add(item)
        session.commit()
        return redirect(url_for("consignment_list.consignment_list_detail", consignment_list_id=item.consignment_list_id))
    finally:
        session.close()


@bp.route("/<int:consignment_list_id>/edit", methods=["GET", "POST"])
def consignment_list_edit(consignment_list_id: int):
    session = _get_session()
    try:
        item = session.get(ConsignmentList, consignment_list_id)
        if item is None:
            return "Not found", 404
        if request.method == "GET":
            return render_template("consignment_list/form.html", item=item)
        item.customer_id = int(request.form.get("customer_id") or 0)
        item.part_id = int(request.form.get("part_id") or 0)
        item.quantity = int(request.form.get("quantity") or 0)
        session.commit()
        return redirect(
            url_for(
                "consignment_list.consignment_list_detail",
                consignment_list_id=consignment_list_id,
            )
        )
    finally:
        session.close()


@bp.route("/<int:consignment_list_id>/delete", methods=["POST"])
def consignment_list_delete(consignment_list_id: int):
    session = _get_session()
    try:
        item = session.get(ConsignmentList, consignment_list_id)
        if item is None:
            return "Not found", 404
        session.delete(item)
        session.commit()
        return redirect(url_for("consignment_list.consignment_list"))
    finally:
        session.close()
