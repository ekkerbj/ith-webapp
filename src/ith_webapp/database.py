from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def _engine_options(database_url: str) -> dict[str, object]:
    if database_url.startswith("postgresql"):
        return {
            "pool_pre_ping": True,
            "pool_size": 5,
            "max_overflow": 10,
        }
    return {}


def create_session_factory(database_url: str = "sqlite:///:memory:") -> sessionmaker[Session]:
    engine = create_engine(database_url, echo=False, **_engine_options(database_url))
    return sessionmaker(bind=engine)


def init_db(database_url: str = "sqlite:///:memory:") -> tuple[sessionmaker[Session], "create_engine"]:
    engine = create_engine(database_url, echo=False, **_engine_options(database_url))
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    return factory, engine
