from pathlib import Path
import tomllib


def test_cloud_run_deployment_artifacts_are_defined():
    root = Path(__file__).resolve().parents[2]
    pyproject = tomllib.loads((root / "pyproject.toml").read_text())
    dependencies = pyproject["project"]["dependencies"]

    assert (root / "Dockerfile").exists()
    assert (root / "firebase.json").exists()
    assert (root / "cloudbuild.yaml").exists()
    assert (root / "src/ith_webapp/wsgi.py").exists()
    assert any(dep.startswith("gunicorn") for dep in dependencies)
    assert any(dep.startswith("psycopg") for dep in dependencies)
