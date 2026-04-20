from pathlib import Path
import mimetypes

from flask import (
    Blueprint,
    abort,
    current_app,
    redirect,
    render_template,
    render_template_string,
    request,
    send_file,
    url_for,
)
from werkzeug.utils import secure_filename
from sqlalchemy import or_

from ith_webapp.models.part import Part
from ith_webapp.models.parts_sold import PartsSold
from ith_webapp.services.barcode_generation import generate_code128_svg
from ith_webapp.services.pagination import paginate_query
from ith_webapp.views.session import get_session

bp = Blueprint("parts", __name__, url_prefix="/parts")

_LABEL_FORMATS = {
    "short": {"title": "Short Label", "class_name": "label-short"},
    "long": {"title": "Long Label", "class_name": "label-long"},
    "multi": {"title": "Multi Label", "class_name": "label-multi"},
    "kit": {"title": "Kit Label", "class_name": "label-kit"},
    "custom": {"title": "Custom Label", "class_name": "label-custom"},
}


def _get_session():
    return get_session()


def _label_format(name: str | None) -> dict[str, str]:
    if not name:
        return _LABEL_FORMATS["short"]
    return _LABEL_FORMATS.get(name.lower(), _LABEL_FORMATS["short"])


def _attachment_root() -> Path:
    root = current_app.config.get("PART_ATTACHMENT_STORAGE_ROOT")
    if root is not None:
        return Path(root)
    return Path(current_app.instance_path) / "part_attachments"


def _part_attachment_directory(part_id: int) -> Path:
    return _attachment_root() / str(part_id)


def _part_attachment_paths(part_id: int) -> list[Path]:
    directory = _part_attachment_directory(part_id)
    if not directory.exists():
        return []
    return sorted(path for path in directory.iterdir() if path.is_file())


def _attachment_metadata(path: Path) -> dict[str, str | bool]:
    mimetype, _ = mimetypes.guess_type(path.name)
    return {
        "name": path.name,
        "url": f"/parts/{path.parent.name}/attachments/{path.name}",
        "is_image": bool(mimetype and mimetype.startswith("image/")),
    }


def _render_part_detail(part: Part, sales, attachments):
    return render_template_string(
        """
        {% extends "base.html" %}
        {% block title %}{{ part.part_number }} - ITH{% endblock %}
        {% block content %}
        <h1>{{ part.part_number }}</h1>

        <p>{{ part.description or "" }}</p>
        <p>Active: {{ "Yes" if part.active else "No" }}</p>

        <section>
          <h2>Attachments</h2>
          <form method="post" action="{{ url_for('parts.part_attachment_upload', part_id=part.part_id) }}" enctype="multipart/form-data">
            <label>
              File
              <input type="file" name="file" required>
            </label>
            <button type="submit">Upload</button>
          </form>
          {% if attachments %}
          <ul>
            {% for attachment in attachments %}
            <li>
              <a href="{{ attachment.url }}">{{ attachment.name }}</a>
              {% if attachment.is_image %}
              <div><img src="{{ attachment.url }}" alt="{{ attachment.name }}" style="max-width: 320px;"></div>
              {% endif %}
            </li>
            {% endfor %}
          </ul>
          {% else %}
          <p>No attachments found.</p>
          {% endif %}
        </section>

        <a href="{{ url_for('parts.part_sold_history', part_id=part.part_id) }}">Sold history</a>
        {% endblock %}
        """,
        part=part,
        sales=sales,
        attachments=attachments,
    )


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
        attachments = [_attachment_metadata(path) for path in _part_attachment_paths(part_id)]
        return _render_part_detail(part, sales, attachments)
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


@bp.route("/<int:part_id>/attachments", methods=["POST"])
def part_attachment_upload(part_id: int):
    session = _get_session()
    try:
        part = session.get(Part, part_id)
        if part is None:
            return "Not found", 404
        upload = request.files.get("file")
        if upload is None or not upload.filename:
            abort(400, description="A file upload is required")
        filename = secure_filename(upload.filename)
        if not filename:
            abort(400, description="Invalid file name")
        directory = _part_attachment_directory(part_id)
        directory.mkdir(parents=True, exist_ok=True)
        upload.save(directory / filename)
        return redirect(url_for("parts.part_detail", part_id=part_id))
    finally:
        session.close()


@bp.route("/<int:part_id>/attachments/<path:filename>")
def part_attachment_download(part_id: int, filename: str):
    session = _get_session()
    try:
        part = session.get(Part, part_id)
        if part is None:
            return "Not found", 404
    finally:
        session.close()

    safe_name = secure_filename(filename)
    if not safe_name:
        return "Not found", 404
    path = _part_attachment_directory(part_id) / safe_name
    if not path.exists():
        return "Not found", 404
    mimetype, _ = mimetypes.guess_type(path.name)
    as_attachment = not (mimetype and mimetype.startswith("image/"))
    return send_file(
        path,
        as_attachment=as_attachment,
        download_name=path.name if as_attachment else None,
        mimetype=mimetype,
    )


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
