from flask import g
from sqlalchemy import create_engine

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.views.session import get_session
from ith_webapp.views.session import register_session_middleware


def test_request_session_is_shared_and_closed_after_response():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    events = []

    class TrackingSession:
        def __init__(self):
            events.append("created")

        def close(self):
            events.append("closed")

    app.config["SESSION_FACTORY"] = lambda: TrackingSession()
    register_session_middleware(app)

    @app.route("/session-check")
    def session_check():
        first = get_session()
        second = get_session()
        assert first is second
        assert g.session is first
        return "ok"

    response = app.test_client().get("/session-check")

    assert response.status_code == 200
    assert events == ["created", "closed"]
