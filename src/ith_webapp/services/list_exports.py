from collections.abc import Sequence
import csv
from io import StringIO

from flask import Response, abort


def _export_filename(title: str, extension: str) -> str:
    slug = title.lower().replace(" ", "_")
    return f"{slug}.{extension}"


def build_list_export_response(
    *,
    title: str,
    headers: Sequence[str],
    rows: Sequence[Sequence[object]],
    export_format: str | None,
) -> Response | None:
    if not export_format:
        return None

    normalized_format = export_format.lower()
    if normalized_format == "csv":
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(headers)
        writer.writerows(rows)
        response = Response(buffer.getvalue(), mimetype="text/csv")
        response.headers["Content-Disposition"] = (
            f'attachment; filename="{_export_filename(title, "csv")}"'
        )
        return response

    if normalized_format in {"excel", "xls"}:
        buffer = StringIO()
        writer = csv.writer(buffer, delimiter="\t")
        writer.writerow(headers)
        writer.writerows(rows)
        response = Response(buffer.getvalue(), mimetype="application/vnd.ms-excel")
        response.headers["Content-Disposition"] = (
            f'attachment; filename="{_export_filename(title, "xls")}"'
        )
        return response

    abort(400, description="Unsupported export format")
