from flask import Blueprint, current_app, render_template, render_template_string, request, url_for
from sqlalchemy import or_

from ith_webapp.models.part import Part
from ith_webapp.models.parts_sold import PartsSold
from ith_webapp.services.barcode_generation import generate_code128_svg
from ith_webapp.services.pagination import paginate_query

bp = Blueprint("parts", __name__, url_prefix="/parts")

_LABEL_FORMATS = {
    "short": {"title": "Short Label", "class_name": "label-short"},
    "long": {"title": "Long Label", "class_name": "label-long"},
    "multi": {"title": "Multi Label", "class_name": "label-multi"},
    "kit": {"title": "Kit Label", "class_name": "label-kit"},
    "custom": {"title": "Custom Label", "class_name": "label-custom"},
}


def _get_session():
    factory = current_app.config["SESSION_FACTORY"]
    return factory()


def _label_format(name: str | None) -> dict[str, str]:
    if not name:
        return _LABEL_FORMATS["short"]
    return _LABEL_FORMATS.get(name.lower(), _LABEL_FORMATS["short"])


@bp.route("/")
def part_list():
    session = _get_session()
    try:
        query = (request.args.get("q") or "").strip()
        items_query = session.query(Part)
        if query:
            like = f"%{query}%"
            items_query = items_query.filter(
                or_(
                    Part.part_number.ilike(like),
                    Part.description.ilike(like),
                )
            )
        items, pagination = paginate_query(
            items_query.order_by(Part.part_id),
            "parts.part_list",
            request.args,
            request.args.get("page", 1, type=int),
            request.args.get(
                "page_size",
                current_app.config["LIST_PAGE_SIZE"],
                type=int,
            ),
        )
        rows = [
            {
                "url": url_for("parts.part_detail", part_id=item.part_id),
                "values": [
                    item.part_number,
                    item.description or "",
                    "Yes" if item.active else "No",
                ],
            }
            for item in items
        ]
        return render_template(
            "crud/list.html",
            title="Parts",
            heading="Parts",
            headers=("Item Code", "Description", "Active"),
            rows=rows,
            pagination=pagination,
            empty_message="No parts found.",
        )
    finally:
        session.close()


@bp.route("/<int:part_id>")
def part_detail(part_id: int):
    session = _get_session()
    try:
        part = session.get(Part, part_id)
        if part is None:
            return "Not found", 404
        sales = (
            session.query(PartsSold)
            .filter(PartsSold.part_id == part_id)
            .order_by(PartsSold.id)
            .all()
        )
        return render_template("parts/detail.html", part=part, sales=sales)
    finally:
        session.close()


@bp.route("/<int:part_id>/sold-history")
def part_sold_history(part_id: int):
    session = _get_session()
    try:
        part = session.get(Part, part_id)
        if part is None:
            return "Not found", 404
        sales = (
            session.query(PartsSold)
            .filter(PartsSold.part_id == part_id)
            .order_by(PartsSold.id)
            .all()
        )
        return render_template("parts/sold_history.html", part=part, sales=sales)
    finally:
        session.close()


@bp.route("/<int:part_id>/labels")
def part_labels(part_id: int):
    session = _get_session()
    try:
        part = session.get(Part, part_id)
        if part is None:
            return "Not found", 404
        label_format = _label_format(request.args.get("format"))
        warehouse = request.args.get("warehouse") or "Warehouse not specified"
        barcode_svg = generate_code128_svg(part.part_number).decode("utf-8")
        return render_template_string(
            """
            {% extends "base.html" %}
            {% block title %}Part Labels - ITH{% endblock %}
            {% block content %}
            <h1>Part Labels</h1>
            <p>Format: {{ label_format.title }}</p>
            <section class="part-label-sheet part-label-sheet--{{ label_format.class_name }}">
              <article class="part-label">
                <div class="part-label__barcode">{{ barcode_svg | safe }}</div>
                <dl>
                  <div><dt>Item Code</dt><dd>{{ part.part_number }}</dd></div>
                  <div><dt>Description</dt><dd>{{ part.description or "" }}</dd></div>
                  <div><dt>Warehouse</dt><dd>{{ warehouse }}</dd></div>
                </dl>
              </article>
            </section>
            <p><a href="{{ url_for('parts.part_detail', part_id=part.part_id) }}">Back to part</a></p>
            {% endblock %}
            """,
            part=part,
            barcode_svg=barcode_svg,
            warehouse=warehouse,
            label_format=label_format,
            url_for=url_for,
        )
    finally:
        session.close()
