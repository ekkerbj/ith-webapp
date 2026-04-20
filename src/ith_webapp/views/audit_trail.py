from flask import Blueprint, current_app, render_template

from ith_webapp.services.audit_trail import get_audit_history

bp = Blueprint("audit_trail", __name__, url_prefix="/audit-trail")


def _get_session():
    factory = current_app.config["SESSION_FACTORY"]
    return factory()


@bp.route("/<table_name>/<int:record_id>")
def audit_history(table_name: str, record_id: int):
    session = _get_session()
    try:
        entries = get_audit_history(session, table_name=table_name, record_id=record_id)
        return render_template(
            "audit_trail/history.html",
            table_name=table_name,
            record_id=record_id,
            entries=entries,
        )
    finally:
        session.close()
