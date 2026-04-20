from flask import Blueprint, Response, current_app, render_template, render_template_string, request
from sqlalchemy import or_

from ith_webapp.models.packing_list import PackingList
from ith_webapp.services.list_exports import build_list_export_response
from ith_webapp.services.barcode_generation import generate_code128_svg
from ith_webapp.services.pagination import paginate_query
from ith_webapp.services.table_sorting import apply_sorting, build_sortable_columns
from ith_webapp.views.session import get_session

bp = Blueprint('packing_list_workflow', __name__)


def _get_session():
    return get_session()


def _render_customer_specific_label(packing_list: PackingList, label_title: str) -> str:
    barcode_svg = generate_code128_svg(str(packing_list.id)).decode("utf-8")
    return render_template_string(
        """
        {% extends "base.html" %}
        {% block title %}{{ label_title }} - ITH{% endblock %}
        {% block content %}
        <h1>{{ label_title }}</h1>
        <section class="packing-list-label">
          <div class="packing-list-label__barcode">{{ barcode_svg | safe }}</div>
          <dl>
            <div><dt>Packing List ID</dt><dd>{{ packing_list.id }}</dd></div>
          </dl>
        </section>
        {% endblock %}
        """,
        barcode_svg=barcode_svg,
        label_title=label_title,
        packing_list=packing_list,
    )


@bp.route('/packing-lists/')
def packing_list_index():
    session = _get_session()
    try:
        query_text = (request.args.get("q") or "").strip()
        items_query = session.query(PackingList)
        if query_text:
            like = f"%{query_text}%"
            items_query = items_query.filter(
                or_(
                    PackingList.customer_name.ilike(like),
                    PackingList.packing_date.ilike(like),
                )
            )
        items_query, current_sort, current_direction = apply_sorting(
            items_query,
            request.args,
            {
                "customer_name": PackingList.customer_name,
                "packing_date": PackingList.packing_date,
                "id": PackingList.id,
            },
            "id",
        )
        headers = [
            "Customer",
            "Packing Date",
            "ID",
        ]
        export_rows = [
            [
                packing_list.customer_name or "",
                packing_list.packing_date or "",
                packing_list.id,
            ]
            for packing_list in items_query.all()
        ]
        export_response = build_list_export_response(
            title="Packing Lists",
            headers=headers,
            rows=export_rows,
            export_format=request.args.get("format"),
        )
        if export_response is not None:
            return export_response
        packing_lists, pagination = paginate_query(
            items_query,
            "packing_list_workflow.packing_list_index",
            request.args,
            request.args.get("page", 1, type=int),
            request.args.get(
                "page_size",
                current_app.config["LIST_PAGE_SIZE"],
                type=int,
            ),
        )
        columns = build_sortable_columns(
            "packing_list_workflow.packing_list_index",
            request.args,
            (
                ("Customer", "customer_name"),
                ("Packing Date", "packing_date"),
                ("ID", "id"),
            ),
            current_sort,
            current_direction,
        )
        rows = [
            {
                "values": [
                    packing_list.customer_name or "",
                    packing_list.packing_date or "",
                    packing_list.id,
                ],
            }
            for packing_list in packing_lists
        ]
        return render_template(
            "crud/list.html",
            title="Packing Lists",
            heading="Packing Lists",
            columns=columns,
            rows=rows,
            pagination=pagination,
            empty_message="No packing lists found.",
        )
    finally:
        session.close()


@bp.route('/packing-lists/ready-to-produce')
def ready_to_produce():
    return Response('Not Implemented', status=501)

@bp.route('/packing-lists/ready-to-ship')
def ready_to_ship():
    return Response('Not Implemented', status=501)


@bp.route('/packing-lists/<int:packing_list_id>/labels/cat')
def cat_bar_code_label(packing_list_id: int):
    session = _get_session()
    try:
        packing_list = session.get(PackingList, packing_list_id)
        if packing_list is None:
            return "Not found", 404
        return _render_customer_specific_label(packing_list, "CAT Bar Code Label")
    finally:
        session.close()


@bp.route('/packing-lists/<int:packing_list_id>/labels/zf')
def zf_bar_code_label(packing_list_id: int):
    session = _get_session()
    try:
        packing_list = session.get(PackingList, packing_list_id)
        if packing_list is None:
            return "Not found", 404
        return _render_customer_specific_label(packing_list, "ZF Bar Code Label")
    finally:
        session.close()
