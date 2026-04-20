from flask import Blueprint, current_app, redirect, render_template, request, url_for

from ith_webapp.models.project import Project
from ith_webapp.services.pagination import paginate_query
from ith_webapp.views.session import get_session

bp = Blueprint("projects", __name__, url_prefix="/projects")


def _get_session():
    return get_session()


@bp.route("/")
def project_list():
    session = _get_session()
    try:
        items, pagination = paginate_query(
            session.query(Project).order_by(Project.project_id),
            "projects.project_list",
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
                "url": url_for("projects.project_detail", project_id=item.project_id),
                "values": [
                    item.project_name or "",
                    item.cardcode or "",
                    "Yes" if item.active else "No",
                ],
            }
            for item in items
        ]
        return render_template(
            "crud/list.html",
            title="Projects",
            heading="Projects",
            headers=("Name", "Card Code", "Active"),
            rows=rows,
            pagination=pagination,
            empty_message="No projects found.",
        )
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
