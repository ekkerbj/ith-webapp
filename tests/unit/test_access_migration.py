from decimal import Decimal

import pytest

from ith_webapp.database import Base, init_db
from ith_webapp.models.customer import Customer
from ith_webapp.models.audit_trail import AuditTrail


def test_prepare_access_row_normalizes_source_columns_and_excludes_replication_fields():
    from ith_webapp.services.access_migration import prepare_access_row

    source_row = {
        "customer": "Acme Corp",
        "card code": "C10001",
        "active": "yes",
        "credit limit": "1234.50",
        "s_guid": "ignored",
        "s_collineage": "ignored",
    }

    prepared = prepare_access_row(Customer, source_row)

    assert prepared == {
        "customer_name": "Acme Corp",
        "card_code": "C10001",
        "active": True,
        "credit_limit": Decimal("1234.50"),
    }


def test_prepare_access_row_uses_access_table_label_for_customer_name():
    from ith_webapp.services.access_migration import prepare_access_row

    source_row = {
        "Catalog Customer Name": "Acme Corp",
        "CardCode": "C10001",
        "Active": "yes",
    }

    prepared = prepare_access_row(Customer, source_row, access_table_name="Customer")

    assert prepared["customer_name"] == "Acme Corp"


def test_prepare_access_row_treats_blank_numeric_fields_as_missing():
    from ith_webapp.services.access_migration import prepare_access_row

    source_row = {
        "customer": "Acme Corp",
        "lead id": "",
    }

    prepared = prepare_access_row(Customer, source_row)

    assert prepared["lead_id"] is None


def test_prepare_access_row_maps_audit_trail_fields_from_access_names():
    from ith_webapp.services.access_migration import prepare_access_row

    source_row = {
        "DateTime": "09/28/18 11:34:06",
        "UserName": "sgeorgiev",
        "FormName": "Service Measurements-Gauge",
        "Action": "NEW",
        "RecordID": "2147481106",
        "FieldName": "",
        "OldValue": "",
        "NewValue": "",
    }

    prepared = prepare_access_row(AuditTrail, source_row)

    assert prepared["table_name"] == "Service Measurements-Gauge"


def test_prepare_access_row_maps_lookup_names_from_access_table_label():
    from ith_webapp.models.classification import Classification
    from ith_webapp.services.access_migration import prepare_access_row

    source_row = {
        "Classification": "Panel, Touch",
    }

    prepared = prepare_access_row(Classification, source_row, access_table_name="Classification")

    assert prepared["name"] == "Panel, Touch"


def test_prepare_access_row_skips_blank_required_lookup_names():
    from ith_webapp.models.classification import Classification
    from ith_webapp.services.access_migration import prepare_access_row

    source_row = {"Classification": ""}

    prepared = prepare_access_row(Classification, source_row, access_table_name="Classification")

    assert "name" not in prepared


def test_import_access_data_skips_rows_missing_required_fields(monkeypatch, tmp_path):
    from ith_webapp.commands.import_access import import_access_data
    from ith_webapp.models.classification import Classification
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import sessionmaker

    monkeypatch.setattr(
        "ith_webapp.services.access_migration.list_access_tables",
        lambda _access_file: ["Classification"],
    )
    monkeypatch.setattr(
        "ith_webapp.services.access_migration.export_access_rows",
        lambda _access_file, _table_name: [
            {"Classification ID": "1", "Classification": ""},
            {"Classification ID": "2", "Classification": "Valid"},
        ],
    )

    database_path = tmp_path / "import.db"
    import_access_data(f"sqlite:///{database_path}", "access")

    engine = create_engine(f"sqlite:///{database_path}")
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        names = session.execute(select(Classification.name)).scalars().all()
    finally:
        session.close()

    assert names == ["Valid"]


def test_migration_tables_follow_foreign_key_dependencies():
    from ith_webapp.models import CustomerAddress, Customer, Service, ServiceSub
    from ith_webapp.services.access_migration import migration_tables
    from ith_webapp.database import Base

    tables = migration_tables(Base.metadata)
    table_names = [table.name for table in tables]

    assert table_names.index(Customer.__tablename__) < table_names.index(CustomerAddress.__tablename__)
    assert table_names.index(Service.__tablename__) < table_names.index(ServiceSub.__tablename__)


def test_import_requires_an_empty_database():
    from ith_webapp.models import Customer
    from ith_webapp.services.access_migration import assert_empty_database

    factory, _engine = init_db("sqlite:///:memory:")
    session = factory()
    session.add(Customer(customer_name="Acme Corp", card_code="C10001"))
    session.commit()

    with pytest.raises(RuntimeError, match="target database must be empty before import"):
        assert_empty_database(session, Base.metadata)
    session.close()


def test_import_access_data_populates_a_fresh_sqlite_database(monkeypatch, tmp_path):
    from ith_webapp.commands.import_access import import_access_data
    from ith_webapp.models import Customer
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import sessionmaker

    monkeypatch.setattr(
        "ith_webapp.services.access_migration.list_access_tables",
        lambda _access_file: ["Customer"],
    )
    monkeypatch.setattr(
        "ith_webapp.services.access_migration.export_access_rows",
        lambda _access_file, _table_name: [
            {"customer": "Acme Corp", "card code": "C10001", "active": "yes"}
        ],
    )

    database_path = tmp_path / "import.db"
    import_access_data(f"sqlite:///{database_path}", "access")

    engine = create_engine(f"sqlite:///{database_path}")
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        customer_count = session.execute(select(Customer)).scalars().all()
    finally:
        session.close()

    assert len(customer_count) == 1
