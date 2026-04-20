from datetime import date

from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    render_template_string,
    request,
    url_for,
)

from ith_webapp.models.ith_test_gauge import ITHTestGauge
from ith_webapp.services.barcode_generation import generate_code128_svg
from ith_webapp.services.pagination import paginate_query

bp = Blueprint("ith_test_gauges", __name__, url_prefix="/ith-test-gauges")


def _get_session():
    factory = current_app.config["SESSION_FACTORY"]
    return factory()


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def _render_label(item: ITHTestGauge, label_title: str, due_date_label: str, due_date) -> str:
    barcode_svg = generate_code128_svg(item.serial_number).decode("utf-8")
    return render_template_string(
        """
        {% extends "base.html" %}
        {% block title %}{{ label_title }} - ITH{% endblock %}
        {% block content %}
        <h1>{{ label_title }}</h1>
        <section class="ith-test-gauge-label">
          <div class="ith-test-gauge-label__barcode">{{ barcode_svg | safe }}</div>
          <dl>
            <div><dt>Gauge Name</dt><dd>{{ item.name }}</dd></div>
            <div><dt>Serial Number</dt><dd>{{ item.serial_number }}</dd></div>
            <div><dt>Type</dt><dd>{{ gauge_type }}</dd></div>
            <div><dt>{{ due_date_label }}</dt><dd>{{ due_date }}</dd></div>
          </dl>
        </section>
        <p><a href="{{ url_for('ith_test_gauges.ith_test_gauge_detail', ith_test_gauge_id=item.ith_test_gauge_id) }}">Back to gauge</a></p>
        {% endblock %}
        """,
        item=item,
        barcode_svg=barcode_svg,
        gauge_type=getattr(item.ith_test_gauge_type, "name", "") or "",
        due_date_label=due_date_label,
        due_date=due_date.isoformat() if due_date else "",
        label_title=label_title,
        url_for=url_for,
    )


@bp.route("/")
def ith_test_gauge_list():
    session = _get_session()
    try:
        items, pagination = paginate_query(
            session.query(ITHTestGauge)
            .order_by(ITHTestGauge.ith_test_gauge_id)
            ,
            "ith_test_gauges.ith_test_gauge_list",
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
                "url": url_for(
                    "ith_test_gauges.ith_test_gauge_detail",
                    ith_test_gauge_id=item.ith_test_gauge_id,
                ),
                "values": [
                    getattr(item.ith_test_gauge_type, "name", "") or "",
                    item.name,
                    item.serial_number,
                    item.calibration_due_date or "",
                    item.certification_due_date or "",
                ],
            }
            for item in items
        ]
        return render_template(
            "crud/list.html",
            title="ITH Test Gauges",
            heading="ITH Test Gauges",
            headers=("Type", "Name", "Serial Number", "Calibration Due", "Certification Due"),
            rows=rows,
            pagination=pagination,
            empty_message="No ITH test gauges found.",
        )
    finally:
        session.close()


@bp.route("/<int:ith_test_gauge_id>")
def ith_test_gauge_detail(ith_test_gauge_id: int):
    session = _get_session()
    try:
        item = session.get(ITHTestGauge, ith_test_gauge_id)
        if item is None:
            return "Not found", 404
        return render_template("ith_test_gauges/detail.html", item=item)
    finally:
        session.close()


@bp.route("/new", methods=["GET", "POST"])
def ith_test_gauge_create():
    if request.method == "GET":
        return render_template("ith_test_gauges/form.html")

    session = _get_session()
    try:
        item = ITHTestGauge(
            ith_test_gauge_type_id=int(request.form.get("ith_test_gauge_type_id") or 0),
            name=request.form.get("name") or None,
            serial_number=request.form.get("serial_number") or None,
            calibration_due_date=_parse_date(request.form.get("calibration_due_date")),
            certification_due_date=_parse_date(
                request.form.get("certification_due_date")
            ),
        )
        session.add(item)
        session.commit()
        return redirect(
            url_for("ith_test_gauges.ith_test_gauge_detail", ith_test_gauge_id=item.ith_test_gauge_id)
        )
    finally:
        session.close()


@bp.route("/<int:ith_test_gauge_id>/edit", methods=["GET", "POST"])
def ith_test_gauge_edit(ith_test_gauge_id: int):
    session = _get_session()
    try:
        item = session.get(ITHTestGauge, ith_test_gauge_id)
        if item is None:
            return "Not found", 404
        if request.method == "GET":
            return render_template("ith_test_gauges/form.html", item=item)
        item.ith_test_gauge_type_id = int(
            request.form.get("ith_test_gauge_type_id") or 0
        )
        item.name = request.form.get("name") or None
        item.serial_number = request.form.get("serial_number") or None
        item.calibration_due_date = _parse_date(request.form.get("calibration_due_date"))
        item.certification_due_date = _parse_date(
            request.form.get("certification_due_date")
        )
        session.commit()
        return redirect(
            url_for("ith_test_gauges.ith_test_gauge_detail", ith_test_gauge_id=ith_test_gauge_id)
        )
    finally:
        session.close()


@bp.route("/<int:ith_test_gauge_id>/delete", methods=["POST"])
def ith_test_gauge_delete(ith_test_gauge_id: int):
    session = _get_session()
    try:
        item = session.get(ITHTestGauge, ith_test_gauge_id)
        if item is None:
            return "Not found", 404
        session.delete(item)
        session.commit()
        return redirect(url_for("ith_test_gauges.ith_test_gauge_list"))
    finally:
        session.close()


@bp.route("/<int:ith_test_gauge_id>/labels/calibration")
def ith_test_gauge_calibration_label(ith_test_gauge_id: int):
    session = _get_session()
    try:
        item = session.get(ITHTestGauge, ith_test_gauge_id)
        if item is None:
            return "Not found", 404
        return _render_label(
            item,
            "Gauge Calibration Label",
            "Calibration Due Date",
            item.calibration_due_date,
        )
    finally:
        session.close()


@bp.route("/<int:ith_test_gauge_id>/labels/certification")
def ith_test_gauge_certification_label(ith_test_gauge_id: int):
    session = _get_session()
    try:
        item = session.get(ITHTestGauge, ith_test_gauge_id)
        if item is None:
            return "Not found", 404
        return _render_label(
            item,
            "Force Certification Label",
            "Certification Due Date",
            item.certification_due_date,
        )
    finally:
        session.close()
