from flask import Blueprint, Response, current_app, render_template_string, request

from ith_webapp.models.packing_list import PackingList
from ith_webapp.services.barcode_generation import generate_code128_svg

bp = Blueprint('packing_list_workflow', __name__)


def _get_session():
    factory = current_app.config["SESSION_FACTORY"]
    return factory()


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
        packing_lists = session.query(PackingList).order_by(PackingList.id).all()
        query = (request.args.get("q") or "").strip().lower()
        if query:
            packing_lists = [
                packing_list
                for packing_list in packing_lists
                if query in (packing_list.customer_name or "").lower()
                or query in (packing_list.packing_date or "").lower()
            ]
        return render_template_string(
            """
            {% extends "base.html" %}
            {% block title %}Packing Lists - ITH{% endblock %}
            {% block content %}
            <h1>Packing Lists</h1>
            <table>
              <thead>
                <tr><th>Customer</th><th>Packing Date</th><th>ID</th></tr>
              </thead>
              <tbody>
                {% if packing_lists %}
                {% for packing_list in packing_lists %}
                <tr>
                  <td>{{ packing_list.customer_name or "" }}</td>
                  <td>{{ packing_list.packing_date or "" }}</td>
                  <td>{{ packing_list.id }}</td>
                </tr>
                {% endfor %}
                {% else %}
                <tr><td colspan="3">No packing lists found.</td></tr>
                {% endif %}
              </tbody>
            </table>
            {% endblock %}
            """,
            packing_lists=packing_lists,
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
