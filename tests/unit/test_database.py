from ith_webapp.database import create_session_factory


def test_create_session_factory_enables_postgresql_pooling(monkeypatch):
    captured = {}

    def fake_create_engine(database_url, **kwargs):
        captured["database_url"] = database_url
        captured["kwargs"] = kwargs
        return object()

    monkeypatch.setattr("ith_webapp.database.create_engine", fake_create_engine)

    create_session_factory("postgresql+psycopg://user:pass@db.example.com/ith")

    assert captured["database_url"] == "postgresql+psycopg://user:pass@db.example.com/ith"
    assert captured["kwargs"]["pool_pre_ping"] is True
    assert captured["kwargs"]["pool_size"] == 5
    assert captured["kwargs"]["max_overflow"] == 10
