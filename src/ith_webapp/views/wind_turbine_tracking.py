from dataclasses import dataclass

from flask import Blueprint, current_app, redirect, render_template, request, url_for

from ith_webapp.models.site_gas_turbine import SiteGasTurbine
from ith_webapp.models.site_wind_gas import SiteWindGas
from ith_webapp.models.site_wind_turbine import SiteWindTurbine
from ith_webapp.models.wind_turbine_lead import WindTurbineLead
from ith_webapp.models.wind_turbine_lead_detail import WindTurbineLeadDetail


@dataclass(frozen=True)
class CrudConfig:
    title: str
    endpoint_prefix: str
    list_endpoint: str
    detail_endpoint: str
    model: type
    id_attr: str
    list_columns: tuple[tuple[str, str], ...]
    detail_rows: tuple[tuple[str, str], ...]
    form_fields: tuple[tuple[str, str, str, bool], ...]


def _get_session():
    factory = current_app.config["SESSION_FACTORY"]
    return factory()


def _register_crud_routes(bp: Blueprint, config: CrudConfig) -> None:
    def list_view():
        session = _get_session()
        try:
            items = session.query(config.model).order_by(
                getattr(config.model, config.id_attr)
            )
            rows = [
                {
                    "url": url_for(config.detail_endpoint, **{config.id_attr: getattr(item, config.id_attr)}),
                    "values": [_display_value(getattr(item, attr)) for _, attr in config.list_columns],
                }
                for item in items
            ]
            return render_template(
                "crud/list.html",
                title=config.title,
                heading=config.title,
                list_url=url_for(config.list_endpoint),
                new_url=url_for(f"{config.endpoint_prefix}.create"),
                headers=[label for label, _ in config.list_columns],
                rows=rows,
            )
        finally:
            session.close()

    def detail_view(**kwargs):
        session = _get_session()
        try:
            item = session.get(config.model, kwargs[config.id_attr])
            if item is None:
                return "Not found", 404
            rows = [
                (label, _display_value(getattr(item, attr)))
                for label, attr in config.detail_rows
            ]
            related_rows = []
            if hasattr(item, "details") and item.details:
                related_rows = [
                    (f"Detail {index}", detail.notes or "")
                    for index, detail in enumerate(item.details, start=1)
                ]
            return render_template(
                "crud/detail.html",
                title=config.title,
                heading=getattr(item, config.detail_rows[0][1]) or config.title,
                item=item,
                rows=rows,
                related_rows=related_rows,
                list_url=url_for(config.list_endpoint),
                edit_url=url_for(f"{config.endpoint_prefix}.edit", **{config.id_attr: getattr(item, config.id_attr)}),
                delete_url=url_for(f"{config.endpoint_prefix}.delete", **{config.id_attr: getattr(item, config.id_attr)}),
            )
        finally:
            session.close()

    def create_view():
        if request.method == "GET":
            return render_template(
                "crud/form.html",
                title=config.title,
                heading=f"New {config.title}",
                list_url=url_for(config.list_endpoint),
                fields=[(label, name, field_type, required, "") for label, name, field_type, required in config.form_fields],
            )

        session = _get_session()
        try:
            item = config.model(**_form_values(config.form_fields))
            session.add(item)
            session.commit()
            return redirect(url_for(config.detail_endpoint, **{config.id_attr: getattr(item, config.id_attr)}))
        finally:
            session.close()

    def edit_view(**kwargs):
        session = _get_session()
        try:
            item = session.get(config.model, kwargs[config.id_attr])
            if item is None:
                return "Not found", 404
            if request.method == "GET":
                return render_template(
                    "crud/form.html",
                    title=config.title,
                    heading=f"Edit {config.title}",
                    list_url=url_for(config.list_endpoint),
                    fields=[
                    (
                        label,
                        name,
                        field_type,
                        required,
                        getattr(item, name) if getattr(item, name) is not None else "",
                    )
                        for label, name, field_type, required in config.form_fields
                    ],
                )
            for _, name, field_type, _ in config.form_fields:
                setattr(item, name, _coerce_value(name, field_type))
            session.commit()
            return redirect(url_for(config.detail_endpoint, **{config.id_attr: getattr(item, config.id_attr)}))
        finally:
            session.close()

    def delete_view(**kwargs):
        session = _get_session()
        try:
            item = session.get(config.model, kwargs[config.id_attr])
            if item is None:
                return "Not found", 404
            session.delete(item)
            session.commit()
            return redirect(url_for(config.list_endpoint))
        finally:
            session.close()

    bp.add_url_rule("/", endpoint="list", view_func=list_view)
    bp.add_url_rule("/<int:%s>" % config.id_attr, endpoint="detail", view_func=detail_view)
    bp.add_url_rule("/new", methods=["GET", "POST"], endpoint="create", view_func=create_view)
    bp.add_url_rule(
        "/<int:%s>/edit" % config.id_attr,
        methods=["GET", "POST"],
        endpoint="edit",
        view_func=edit_view,
    )
    bp.add_url_rule(
        "/<int:%s>/delete" % config.id_attr,
        methods=["POST"],
        endpoint="delete",
        view_func=delete_view,
    )


def _coerce_value(name: str, field_type: str, required: bool = False):
    if field_type == "number":
        raw = request.form.get(name)
        if raw in (None, ""):
            return 0 if required else None
        return int(raw)
    return request.form.get(name) or None


def _display_value(value):
    return "" if value is None else value


def _form_values(fields):
    return {name: _coerce_value(name, field_type) for _, name, field_type, _ in fields}


site_gas_turbines_bp = Blueprint("sites_gas_turbines", __name__, url_prefix="/sites-gas-turbines")
_register_crud_routes(
    site_gas_turbines_bp,
    CrudConfig(
        title="Sites Gas Turbine",
        endpoint_prefix="sites_gas_turbines",
        list_endpoint="sites_gas_turbines.list",
        detail_endpoint="sites_gas_turbines.detail",
        model=SiteGasTurbine,
        id_attr="site_gas_turbine_id",
        list_columns=(
            ("Site Name", "site_name"),
            ("Customer", "customer_name"),
            ("Location", "location"),
        ),
        detail_rows=(
            ("Site Name", "site_name"),
            ("Customer", "customer_name"),
            ("Location", "location"),
            ("Notes", "notes"),
        ),
        form_fields=(
            ("Site Name", "site_name", "text", True),
            ("Customer", "customer_name", "text", False),
            ("Location", "location", "text", False),
            ("Notes", "notes", "text", False),
        ),
    ),
)

site_wind_turbines_bp = Blueprint("sites_wind_turbines", __name__, url_prefix="/sites-wind-turbines")
_register_crud_routes(
    site_wind_turbines_bp,
    CrudConfig(
        title="Sites Wind Turbine",
        endpoint_prefix="sites_wind_turbines",
        list_endpoint="sites_wind_turbines.list",
        detail_endpoint="sites_wind_turbines.detail",
        model=SiteWindTurbine,
        id_attr="site_wind_turbine_id",
        list_columns=(
            ("Site Name", "site_name"),
            ("Customer", "customer_name"),
            ("Location", "location"),
        ),
        detail_rows=(
            ("Site Name", "site_name"),
            ("Customer", "customer_name"),
            ("Location", "location"),
            ("Notes", "notes"),
        ),
        form_fields=(
            ("Site Name", "site_name", "text", True),
            ("Customer", "customer_name", "text", False),
            ("Location", "location", "text", False),
            ("Notes", "notes", "text", False),
        ),
    ),
)

site_wind_gas_bp = Blueprint("sites_wind_gas", __name__, url_prefix="/sites-wind-gas")
_register_crud_routes(
    site_wind_gas_bp,
    CrudConfig(
        title="Sites Wind Gas",
        endpoint_prefix="sites_wind_gas",
        list_endpoint="sites_wind_gas.list",
        detail_endpoint="sites_wind_gas.detail",
        model=SiteWindGas,
        id_attr="site_wind_gas_id",
        list_columns=(
            ("Site Name", "site_name"),
            ("Wind Units", "wind_units"),
            ("Gas Units", "gas_units"),
        ),
        detail_rows=(
            ("Site Name", "site_name"),
            ("Wind Units", "wind_units"),
            ("Gas Units", "gas_units"),
            ("Location", "location"),
            ("Notes", "notes"),
        ),
        form_fields=(
            ("Site Name", "site_name", "text", True),
            ("Wind Units", "wind_units", "number", False),
            ("Gas Units", "gas_units", "number", False),
            ("Location", "location", "text", False),
            ("Notes", "notes", "text", False),
        ),
    ),
)

wind_turbine_leads_bp = Blueprint("wind_turbine_leads", __name__, url_prefix="/wind-turbine-leads")
_register_crud_routes(
    wind_turbine_leads_bp,
    CrudConfig(
        title="Wind Turbine Leads",
        endpoint_prefix="wind_turbine_leads",
        list_endpoint="wind_turbine_leads.list",
        detail_endpoint="wind_turbine_leads.detail",
        model=WindTurbineLead,
        id_attr="wind_turbine_lead_id",
        list_columns=(
            ("Customer", "customer_name"),
            ("Contact", "contact_name"),
            ("Status", "status"),
        ),
        detail_rows=(
            ("Customer", "customer_name"),
            ("Contact", "contact_name"),
            ("Phone", "phone"),
            ("Email", "email"),
            ("Status", "status"),
            ("Notes", "notes"),
        ),
        form_fields=(
            ("Customer", "customer_name", "text", True),
            ("Contact", "contact_name", "text", False),
            ("Phone", "phone", "text", False),
            ("Email", "email", "email", False),
            ("Status", "status", "text", False),
            ("Notes", "notes", "text", False),
        ),
    ),
)

wind_turbine_lead_details_bp = Blueprint(
    "wind_turbine_leads_details", __name__, url_prefix="/wind-turbine-leads-details"
)
_register_crud_routes(
    wind_turbine_lead_details_bp,
    CrudConfig(
        title="Wind Turbine Lead Details",
        endpoint_prefix="wind_turbine_leads_details",
        list_endpoint="wind_turbine_leads_details.list",
        detail_endpoint="wind_turbine_leads_details.detail",
        model=WindTurbineLeadDetail,
        id_attr="wind_turbine_lead_detail_id",
        list_columns=(
            ("Lead ID", "wind_turbine_lead_id"),
            ("Notes", "notes"),
        ),
        detail_rows=(
            ("Lead ID", "wind_turbine_lead_id"),
            ("Notes", "notes"),
        ),
        form_fields=(
            ("Lead ID", "wind_turbine_lead_id", "number", True),
            ("Notes", "notes", "text", False),
        ),
    ),
)
