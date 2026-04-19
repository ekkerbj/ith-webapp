from flask import Flask, redirect, url_for


def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)

    if testing:
        app.config["TESTING"] = True
        app.config["DATABASE_URL"] = "sqlite:///:memory:"

    @app.route("/")
    def index():
        return redirect(url_for("customers.customer_list"))

    from ith_webapp.views.customers import bp as customers_bp

    app.register_blueprint(customers_bp)

    return app
