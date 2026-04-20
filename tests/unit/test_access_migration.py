from decimal import Decimal

from ith_webapp.models.customer import Customer


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


def test_migration_tables_follow_foreign_key_dependencies():
    from ith_webapp.models import CustomerAddress, Customer, Service, ServiceSub
    from ith_webapp.services.access_migration import migration_tables
    from ith_webapp.database import Base

    tables = migration_tables(Base.metadata)
    table_names = [table.name for table in tables]

    assert table_names.index(Customer.__tablename__) < table_names.index(CustomerAddress.__tablename__)
    assert table_names.index(Service.__tablename__) < table_names.index(ServiceSub.__tablename__)
