from flask import Flask, current_app, g


_SESSION_G_KEY = "session"


def get_session():
    session = g.get(_SESSION_G_KEY)
    if session is None:
        factory = current_app.config["SESSION_FACTORY"]
        session = factory()
        g.session = session
    return session


def _close_session(_exc: BaseException | None) -> None:
    session = g.pop(_SESSION_G_KEY, None)
    if session is not None:
        session.close()


def register_session_middleware(app: Flask) -> None:
    app.teardown_request(_close_session)
