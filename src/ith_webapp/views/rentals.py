from flask import Blueprint, current_app, redirect, render_template, request, url_for

from ith_webapp.models.customer import Customer
from ith_webapp.models.customer_tools import CustomerTools
from ith_webapp.models.rental import Rental
from ith_webapp.models.rental_status import RentalStatus
from ith_webapp.services.date_filtering import current_month_filter
from ith_webapp.services.pagination import paginate_query
from ith_webapp.services.table_sorting import apply_sorting, build_sortable_columns
from ith_webapp.views.session import get_session

bp = Blueprint("rentals", __name__, url_prefix="/rentals")


def _get_session():
    return get_session()


@bp.route("/")
def rental_list():
    session = _get_session()
    try:
        items_query = (
            session.query(Rental)
            .join(Rental.customer)
            .join(Rental.customer_tools)
            .join(Rental.rental_status)
            .filter(current_month_filter(Rental.rental_date))
        )
        items_query, current_sort, current_direction = apply_sorting(
            items_query,
            request.args,
            {
                "customer_name": Customer.customer_name,
                "serial_number": CustomerTools.serial_number,
                "status": RentalStatus.name,
                "rental_date": Rental.rental_date,
                "rental_id": Rental.rental_id,
            },
            "rental_id",
        )
        items, pagination = paginate_query(
            items_query,
            "rentals.rental_list",
            request.args,
            request.args.get("page", 1, type=int),
            request.args.get(
                "page_size",
                current_app.config["LIST_PAGE_SIZE"],
                type=int,
            ),
        )
        columns = build_sortable_columns(
            "rentals.rental_list",
            request.args,
            (
                ("Customer", "customer_name"),
                ("Tool", "serial_number"),
                ("Status", "status"),
                ("Rental Date", "rental_date"),
            ),
            current_sort,
            current_direction,
        )
        rows = [
            {
                "url": url_for("rentals.rental_detail", rental_id=item.rental_id),
                "values": [
                    getattr(item.customer, "customer_name", "") or "",
                    getattr(item.customer_tools, "serial_number", "") or "",
                    getattr(item.rental_status, "name", "") or "",
                    item.rental_date,
                ],
            }
            for item in items
        ]
        return render_template(
            "crud/list.html",
            title="Rentals",
            heading="Rentals",
            columns=columns,
            rows=rows,
            pagination=pagination,
            empty_message="No rentals found.",
        )
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
