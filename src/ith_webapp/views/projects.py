from flask import Blueprint, current_app, redirect, render_template, request, url_for

from ith_webapp.models.project import Project

bp = Blueprint("projects", __name__, url_prefix="/projects")


def _get_session():
    factory = current_app.config["SESSION_FACTORY"]
    return factory()


@bp.route("/")
def project_list():
    session = _get_session()
    try:
        items = session.query(Project).order_by(Project.project_id).all()
        return render_template("projects/list.html", items=items)
    finally:
        session.close()


@bp.route("/<int:project_id>")
def project_detail(project_id: int):
    session = _get_session()
    try:
        item = session.get(Project, project_id)
        if item is None:
            return "Not found", 404
        return render_template("projects/detail.html", item=item)
    finally:
        session.close()


@bp.route("/new", methods=["GET", "POST"])
def project_create():
    if request.method == "GET":
        return render_template("projects/form.html")

    session = _get_session()
    try:
        item = Project(
            customer_id=int(request.form.get("customer_id") or 0),
            cardcode=request.form.get("cardcode") or None,
            project_name=request.form.get("project_name") or None,
            active=request.form.get("active") == "on",
        )
        session.add(item)
        session.commit()
        return redirect(url_for("projects.project_detail", project_id=item.project_id))
    finally:
        session.close()


@bp.route("/<int:project_id>/edit", methods=["GET", "POST"])
def project_edit(project_id: int):
    session = _get_session()
    try:
        item = session.get(Project, project_id)
        if item is None:
            return "Not found", 404
        if request.method == "GET":
            return render_template("projects/form.html", item=item)
        item.customer_id = int(request.form.get("customer_id") or 0)
        item.cardcode = request.form.get("cardcode") or None
        item.project_name = request.form.get("project_name") or None
        item.active = request.form.get("active") == "on"
        session.commit()
        return redirect(url_for("projects.project_detail", project_id=project_id))
    finally:
        session.close()


@bp.route("/<int:project_id>/delete", methods=["POST"])
def project_delete(project_id: int):
    session = _get_session()
    try:
        item = session.get(Project, project_id)
        if item is None:
            return "Not found", 404
        session.delete(item)
        session.commit()
        return redirect(url_for("projects.project_list"))
    finally:
        session.close()
