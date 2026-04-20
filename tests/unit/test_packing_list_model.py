from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ith_webapp.database import Base
from ith_webapp.models.packing_list import PackingList


def test_packing_list_customer_and_date_fields_persist():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        packing_list = PackingList(
            customer_name="Acme Corp",
            packing_date="2026-04-19",
        )
        session.add(packing_list)
        session.commit()

        result = session.query(PackingList).first()

        assert result is not None
        assert result.customer_name == "Acme Corp"
        assert result.packing_date == "2026-04-19"
