from flask import Flask, redirect, url_for

from ith_webapp.database import Base, create_session_factory


def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)

    if testing:
        app.config["TESTING"] = True
        app.config["DATABASE_URL"] = "sqlite:///:memory:"

    if "SESSION_FACTORY" not in app.config:
        import ith_webapp.models  # noqa: F401 — register models with Base

        database_url = app.config.get("DATABASE_URL", "sqlite:///ith.db")
        factory = create_session_factory(database_url)
        Base.metadata.create_all(factory().get_bind())
        app.config["SESSION_FACTORY"] = factory

    @app.route("/")
    def index():
        return redirect(url_for("customers.customer_list"))

    from ith_webapp.views.customers import bp as customers_bp

    app.register_blueprint(customers_bp)

    return app
