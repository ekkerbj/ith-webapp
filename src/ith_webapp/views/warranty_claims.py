from flask import Blueprint, current_app, redirect, render_template, request, url_for

from ith_webapp.models.warranty_claim import WarrantyClaim, WarrantyClaimQuote
from ith_webapp.services.pagination import paginate_query

bp = Blueprint("warranty_claims", __name__, url_prefix="/warranty-claims")


def _get_session():
    factory = current_app.config["SESSION_FACTORY"]
    return factory()


def _service_ids(raw_value: str | None) -> list[int]:
    if not raw_value:
        return []
    return [int(value.strip()) for value in raw_value.split(",") if value.strip()]


def _sync_quotes(claim: WarrantyClaim, raw_value: str | None) -> None:
    claim.quotes.clear()
    for service_id in _service_ids(raw_value):
        claim.quotes.append(WarrantyClaimQuote(service_id=service_id))


@bp.route("/")
def warranty_claim_list():
    session = _get_session()
    try:
        items, pagination = paginate_query(
            session.query(WarrantyClaim)
            .order_by(WarrantyClaim.warranty_claim_id)
            ,
            "warranty_claims.warranty_claim_list",
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
                "url": url_for(
                    "warranty_claims.warranty_claim_detail",
                    warranty_claim_id=item.warranty_claim_id,
                ),
                "values": [
                    item.claim_number or f"Warranty Claim {item.warranty_claim_id}",
                    getattr(item.customer, "customer_name", "") or "",
                    item.status or "",
                ],
            }
            for item in items
        ]
        return render_template(
            "crud/list.html",
            title="Warranty Claims",
            heading="Warranty Claims",
            headers=("Claim Number", "Customer", "Status"),
            rows=rows,
            pagination=pagination,
            empty_message="No warranty claims found.",
        )
    finally:
        session.close()


@bp.route("/<int:warranty_claim_id>")
def warranty_claim_detail(warranty_claim_id: int):
    session = _get_session()
    try:
        item = session.get(WarrantyClaim, warranty_claim_id)
        if item is None:
            return "Not found", 404
        rows = [
            ("Customer", getattr(item.customer, "customer_name", "") or ""),
            ("Claim Number", item.claim_number or ""),
            ("Status", item.status or ""),
            ("Notes", item.notes or ""),
        ]
        related_rows = [
            (
                f"Quote {index}",
                getattr(quote.service, "cardcode", "") or f"Service {quote.service_id}",
            )
            for index, quote in enumerate(item.quotes, start=1)
        ]
        return render_template(
            "crud/detail.html",
            title="Warranty Claims",
            heading=item.claim_number or "Warranty Claim",
            item=item,
            rows=rows,
            related_rows=related_rows,
            list_url=url_for("warranty_claims.warranty_claim_list"),
            edit_url=url_for(
                "warranty_claims.warranty_claim_edit",
                warranty_claim_id=warranty_claim_id,
            ),
            delete_url=url_for(
                "warranty_claims.warranty_claim_delete",
                warranty_claim_id=warranty_claim_id,
            ),
        )
    finally:
        session.close()


@bp.route("/new", methods=["GET", "POST"])
def warranty_claim_create():
    if request.method == "GET":
        return render_template(
            "crud/form.html",
            title="Warranty Claims",
            heading="New Warranty Claim",
            list_url=url_for("warranty_claims.warranty_claim_list"),
            fields=[
                ("Customer ID", "customer_id", "number", True, ""),
                ("Claim Number", "claim_number", "text", False, ""),
                ("Status", "status", "text", False, ""),
                ("Notes", "notes", "text", False, ""),
                ("Quote Service IDs", "service_ids", "text", False, ""),
            ],
        )

    session = _get_session()
    try:
        item = WarrantyClaim(
            customer_id=int(request.form.get("customer_id") or 0),
            claim_number=request.form.get("claim_number") or None,
            status=request.form.get("status") or None,
            notes=request.form.get("notes") or None,
        )
        session.add(item)
        session.flush()
        _sync_quotes(item, request.form.get("service_ids"))
        session.commit()
        return redirect(
            url_for("warranty_claims.warranty_claim_detail", warranty_claim_id=item.warranty_claim_id)
        )
    finally:
        session.close()


@bp.route("/<int:warranty_claim_id>/edit", methods=["GET", "POST"])
def warranty_claim_edit(warranty_claim_id: int):
    session = _get_session()
    try:
        item = session.get(WarrantyClaim, warranty_claim_id)
        if item is None:
            return "Not found", 404
        if request.method == "GET":
            return render_template(
                "crud/form.html",
                title="Warranty Claims",
                heading="Edit Warranty Claim",
                list_url=url_for("warranty_claims.warranty_claim_list"),
                fields=[
                    ("Customer ID", "customer_id", "number", True, item.customer_id),
                    ("Claim Number", "claim_number", "text", False, item.claim_number or ""),
                    ("Status", "status", "text", False, item.status or ""),
                    ("Notes", "notes", "text", False, item.notes or ""),
                    (
                        "Quote Service IDs",
                        "service_ids",
                        "text",
                        False,
                        ", ".join(str(quote.service_id) for quote in item.quotes),
                    ),
                ],
            )
        item.customer_id = int(request.form.get("customer_id") or 0)
        item.claim_number = request.form.get("claim_number") or None
        item.status = request.form.get("status") or None
        item.notes = request.form.get("notes") or None
        _sync_quotes(item, request.form.get("service_ids"))
        session.commit()
        return redirect(
            url_for("warranty_claims.warranty_claim_detail", warranty_claim_id=warranty_claim_id)
        )
    finally:
        session.close()


@bp.route("/<int:warranty_claim_id>/delete", methods=["POST"])
def warranty_claim_delete(warranty_claim_id: int):
    session = _get_session()
    try:
        item = session.get(WarrantyClaim, warranty_claim_id)
        if item is None:
            return "Not found", 404
        session.delete(item)
        session.commit()
        return redirect(url_for("warranty_claims.warranty_claim_list"))
    finally:
        session.close()
