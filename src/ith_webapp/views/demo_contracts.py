from flask import Blueprint, current_app, redirect, render_template, render_template_string, request, url_for

from ith_webapp.models.rental import Rental
from ith_webapp.services.pagination import paginate_query

bp = Blueprint("demo_contracts", __name__, url_prefix="/demo-contracts")


def _get_session():
    factory = current_app.config["SESSION_FACTORY"]
    return factory()


_LIST_TEMPLATE = """
{% extends "base.html" %}
{% block title %}Demo Contracts - ITH{% endblock %}
{% block content %}
<h1>Demo Contracts</h1>
<table>
  <thead>
    <tr><th>Customer</th><th>Tool</th><th>Status</th><th>Contract Date</th></tr>
  </thead>
  <tbody>
    {% if items %}
    {% for item in items %}
    <tr>
      <td><a href="{{ url_for('demo_contracts.demo_contract_detail', rental_id=item.rental_id) }}">{{ item.customer.customer_name }}</a></td>
      <td>{{ item.customer_tools.serial_number }}</td>
      <td>{{ item.rental_status.name }}</td>
      <td>{{ item.rental_date.isoformat() }}</td>
    </tr>
    {% endfor %}
    {% else %}
    <tr><td colspan="4">(none)</td></tr>
    {% endif %}
  </tbody>
</table>
{% endblock %}
"""

_DETAIL_TEMPLATE = """
{% extends "base.html" %}
{% block title %}Demo Contract - ITH{% endblock %}
{% block content %}
<h1>Demo Contract</h1>
<table>
  <tr><th>Customer</th><td>{{ item.customer.customer_name }}</td></tr>
  <tr><th>Tool</th><td>{{ item.customer_tools.serial_number }}</td></tr>
  <tr><th>Status</th><td>{{ item.rental_status.name }}</td></tr>
  <tr><th>Contract Date</th><td>{{ item.rental_date.isoformat() }}</td></tr>
  <tr><th>Return Date</th><td>{{ item.return_date.isoformat() if item.return_date else "" }}</td></tr>
</table>
<p>
  <a href="{{ url_for('demo_contracts.demo_contract_edit', rental_id=item.rental_id) }}">Edit</a>
  <form method="post" action="{{ url_for('demo_contracts.demo_contract_delete', rental_id=item.rental_id) }}">
    <button type="submit">Delete</button>
  </form>
</p>
<a href="{{ url_for('demo_contracts.demo_contract_list') }}">Back to list</a>
{% endblock %}
"""

_FORM_TEMPLATE = """
{% extends "base.html" %}
{% block title %}{{ "Edit" if item else "New" }} Demo Contract - ITH{% endblock %}
{% block content %}
<h1>{{ "Edit" if item else "New" }} Demo Contract</h1>
<form method="post">
  <label for="customer_id">Customer ID</label>
  <input type="number" id="customer_id" name="customer_id" value="{{ item.customer_id if item else '' }}" required>
  <label for="customer_tools_id">Customer Tool ID</label>
  <input type="number" id="customer_tools_id" name="customer_tools_id" value="{{ item.customer_tools_id if item else '' }}" required>
  <label for="rental_status_id">Status ID</label>
  <input type="number" id="rental_status_id" name="rental_status_id" value="{{ item.rental_status_id if item else '' }}" required>
  <button type="submit">Save</button>
</form>
<a href="{{ url_for('demo_contracts.demo_contract_list') }}">Back to list</a>
{% endblock %}
"""


@bp.route("/")
def demo_contract_list():
    session = _get_session()
    try:
        items, pagination = paginate_query(
            session.query(Rental).order_by(Rental.rental_id),
            "demo_contracts.demo_contract_list",
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
                "url": url_for("demo_contracts.demo_contract_detail", rental_id=item.rental_id),
                "values": [
                    getattr(item.customer, "customer_name", "") or "",
                    getattr(item.customer_tools, "serial_number", "") or "",
                    getattr(item.rental_status, "name", "") or "",
                    item.rental_date.isoformat() if item.rental_date else "",
                ],
            }
            for item in items
        ]
        return render_template(
            "crud/list.html",
            title="Demo Contracts",
            heading="Demo Contracts",
            headers=("Customer", "Tool", "Status", "Contract Date"),
            rows=rows,
            pagination=pagination,
            empty_message="(none)",
        )
    finally:
        session.close()


@bp.route("/<int:rental_id>")
def demo_contract_detail(rental_id: int):
    session = _get_session()
    try:
        item = session.get(Rental, rental_id)
        if item is None:
            return "Not found", 404
        return render_template_string(_DETAIL_TEMPLATE, item=item)
    finally:
        session.close()


@bp.route("/new", methods=["GET", "POST"])
def demo_contract_create():
    if request.method == "GET":
        return render_template_string(_FORM_TEMPLATE)

    session = _get_session()
    try:
        item = Rental(
            customer_id=int(request.form.get("customer_id") or 0),
            customer_tools_id=int(request.form.get("customer_tools_id") or 0),
            rental_status_id=int(request.form.get("rental_status_id") or 0),
        )
        session.add(item)
        session.commit()
        return redirect(url_for("demo_contracts.demo_contract_detail", rental_id=item.rental_id))
    finally:
        session.close()


@bp.route("/<int:rental_id>/edit", methods=["GET", "POST"])
def demo_contract_edit(rental_id: int):
    session = _get_session()
    try:
        item = session.get(Rental, rental_id)
        if item is None:
            return "Not found", 404
        if request.method == "GET":
            return render_template_string(_FORM_TEMPLATE, item=item)
        item.customer_id = int(request.form.get("customer_id") or 0)
        item.customer_tools_id = int(request.form.get("customer_tools_id") or 0)
        item.rental_status_id = int(request.form.get("rental_status_id") or 0)
        session.commit()
        return redirect(url_for("demo_contracts.demo_contract_detail", rental_id=rental_id))
    finally:
        session.close()


@bp.route("/<int:rental_id>/delete", methods=["POST"])
def demo_contract_delete(rental_id: int):
    session = _get_session()
    try:
        item = session.get(Rental, rental_id)
        if item is None:
            return "Not found", 404
        session.delete(item)
        session.commit()
        return redirect(url_for("demo_contracts.demo_contract_list"))
    finally:
        session.close()
