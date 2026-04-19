from flask import Flask

from ith_webapp.database import Base, init_db
from ith_webapp.app import create_app


def test_create_app_returns_flask_instance():
    app = create_app(testing=True)

    assert isinstance(app, Flask)


def test_index_redirects_to_customers(client):
    response = client.get("/")

    assert response.status_code == 302
    assert "/customers" in response.headers["Location"]
