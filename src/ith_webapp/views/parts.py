from flask import Blueprint, current_app, render_template

from ith_webapp.models.part import Part
from ith_webapp.models.parts_sold import PartsSold

bp = Blueprint("parts", __name__, url_prefix="/parts")


def _get_session():
    factory = current_app.config["SESSION_FACTORY"]
    return factory()


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
        return render_template("parts/detail.html", part=part, sales=sales)
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
