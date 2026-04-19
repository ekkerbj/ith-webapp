from ith_webapp.models.project import Project


def test_project_model_fields():
    project = Project(
        project_id=1,
        customer_id=2,
        cardcode="C10001",
        project_name="Test Project",
        active=True,
    )

    assert project.project_id == 1
    assert project.customer_id == 2
    assert project.cardcode == "C10001"
    assert project.project_name == "Test Project"
    assert project.active is True
