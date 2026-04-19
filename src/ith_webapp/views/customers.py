from flask import Blueprint, render_template_string

bp = Blueprint("customers", __name__, url_prefix="/customers")


@bp.route("/")
def customer_list():
    return render_template_string("<h1>Customers</h1>")
