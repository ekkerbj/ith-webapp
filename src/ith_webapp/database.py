from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def create_session_factory(database_url: str = "sqlite:///:memory:") -> sessionmaker[Session]:
    engine = create_engine(database_url, echo=False)
    return sessionmaker(bind=engine)


def init_db(database_url: str = "sqlite:///:memory:") -> tuple[sessionmaker[Session], "create_engine"]:
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    return factory, engine
