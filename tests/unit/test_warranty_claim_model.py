from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ith_webapp.database import Base
from ith_webapp.models import Customer, Service
from ith_webapp.models.warranty_claim import WarrantyClaim, WarrantyClaimQuote


def test_warranty_claim_links_multiple_service_quotes():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        customer = Customer(customer_name="Acme")
        session.add(customer)
        session.flush()

        service_one = Service(customer_id=customer.customer_id, active=True)
        service_two = Service(customer_id=customer.customer_id, active=True)
        session.add_all([service_one, service_two])
        session.flush()

        claim = WarrantyClaim(
            customer_id=customer.customer_id,
            claim_number="WC-1001",
            status="Open",
            notes="Initial claim",
        )
        session.add(claim)
        session.flush()
        session.add_all(
            [
                WarrantyClaimQuote(
                    warranty_claim_id=claim.warranty_claim_id,
                    service_id=service_one.service_id,
                ),
                WarrantyClaimQuote(
                    warranty_claim_id=claim.warranty_claim_id,
                    service_id=service_two.service_id,
                ),
            ]
        )
        session.commit()

        result = session.get(WarrantyClaim, claim.warranty_claim_id)

        assert result is not None
        assert result.claim_number == "WC-1001"
        assert [quote.service_id for quote in result.quotes] == [
            service_one.service_id,
            service_two.service_id,
        ]
