from __future__ import annotations

import argparse
from pathlib import Path

from ith_webapp.database import Base, create_session_factory
from ith_webapp.services.access_migration import assert_empty_database, import_access_data as load_access_data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Import Access data into a local SQLite database")
    parser.add_argument("--database-url", default="sqlite:///ith.db")
    parser.add_argument("--access-dir", default="access")
    return parser


def import_access_data(database_url: str, access_dir: str) -> None:
    import ith_webapp.models  # noqa: F401

    factory = create_session_factory(database_url)
    session = factory()
    try:
        Base.metadata.create_all(session.get_bind())
        assert_empty_database(session, Base.metadata)
        access_file = Path(access_dir) / "ITH_Data_TEST.accdb"
        load_access_data(session, access_file, Base.metadata)
    finally:
        session.close()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    import_access_data(args.database_url, args.access_dir)


if __name__ == "__main__":
    main()
