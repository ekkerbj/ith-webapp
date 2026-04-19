from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models.customer import Customer
from ith_webapp.models.project import Project


def _create_test_app_with_projects(*projects):
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    customer = Customer(customer_name="Acme Corp", card_code="C10001", active=True)
    session.add(customer)
    session.commit()

    for project in projects:
        session.add(project)
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    return app


def test_project_list_renders_project_names():
    app = _create_test_app_with_projects(
        Project(
            customer_id=1,
            cardcode="C10001",
            project_name="Test Project",
            active=True,
        )
    )
    client = app.test_client()

    response = client.get("/projects/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Test Project" in html


def test_project_detail_renders_project_fields():
    app = _create_test_app_with_projects(
        Project(
            customer_id=1,
            cardcode="C10001",
            project_name="Test Project",
            active=True,
        )
    )
    client = app.test_client()

    response = client.get("/projects/1")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Test Project" in html
    assert "C10001" in html


def test_project_detail_returns_404_for_missing_project():
    app = _create_test_app_with_projects()
    client = app.test_client()

    response = client.get("/projects/9999")

    assert response.status_code == 404


def test_project_create_form_renders():
    app = _create_test_app_with_projects()
    client = app.test_client()

    response = client.get("/projects/new")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '<form' in html
    assert 'name="project_name"' in html


def test_project_create_saves_and_redirects():
    app = _create_test_app_with_projects()
    client = app.test_client()

    response = client.post(
        "/projects/new",
        data={
            "customer_id": "1",
            "cardcode": "C10001",
            "project_name": "New Project",
            "active": "on",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/projects/" in response.headers["Location"]


def test_project_edit_form_renders_with_existing_data():
    app = _create_test_app_with_projects(
        Project(
            customer_id=1,
            cardcode="C10001",
            project_name="Test Project",
            active=True,
        )
    )
    client = app.test_client()

    response = client.get("/projects/1/edit")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'value="Test Project"' in html
    assert 'value="C10001"' in html


def test_project_edit_updates_and_redirects():
    app = _create_test_app_with_projects(
        Project(
            customer_id=1,
            cardcode="C10001",
            project_name="Test Project",
            active=True,
        )
    )
    client = app.test_client()

    response = client.post(
        "/projects/1/edit",
        data={
            "customer_id": "1",
            "cardcode": "C20002",
            "project_name": "Updated Project",
            "active": "on",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/projects/1" in response.headers["Location"]

    detail_response = client.get("/projects/1")
    html = detail_response.get_data(as_text=True)
    assert "Updated Project" in html
    assert "C20002" in html


def test_project_delete_removes_project():
    app = _create_test_app_with_projects(
        Project(
            customer_id=1,
            cardcode="C10001",
            project_name="Delete Me",
            active=True,
        ),
        Project(
            customer_id=1,
            cardcode="C10001",
            project_name="Keep Me",
            active=True,
        ),
    )
    client = app.test_client()

    response = client.post("/projects/1/delete", follow_redirects=False)

    assert response.status_code == 302
    assert "/projects/" in response.headers["Location"]

    list_response = client.get("/projects/")
    html = list_response.get_data(as_text=True)
    assert "Delete Me" not in html
    assert "Keep Me" in html
