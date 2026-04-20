from decimal import Decimal

from ith_webapp.repositories.sap_repository import (
    SapCustomerRecord,
    SapCustomerRepository,
    SapItemRecord,
    SapItemRepository,
    SapPriceRepository,
)


def test_set_price_prefers_bp_specific_price_over_lower_tiers():
    from ith_webapp.services.sap_pricing import set_price

    class CustomerAdapter:
        def get_customer(self, card_code: str):
            return SapCustomerRecord(card_code=card_code, card_name="Acme", price_list_num=3)

    class ItemAdapter:
        def get_item(self, item_code: str):
            return SapItemRecord(item_code=item_code, item_name="Widget", purchase_price=Decimal("10.00"))

    class PriceAdapter:
        def get_bp_price(self, card_code: str, item_code: str):
            return Decimal("12.34")

        def get_price_list_price(self, price_list_num: int, item_code: str):
            return Decimal("11.11")

    assert set_price(
        card_code="C10001",
        item_code="A0001",
        customer_repository=CustomerAdapter(),
        item_repository=ItemAdapter(),
        price_repository=PriceAdapter(),
    ) == Decimal("12.34")


def test_set_price_falls_back_to_price_list_when_bp_price_is_missing():
    from ith_webapp.services.sap_pricing import set_price

    class CustomerAdapter:
        def get_customer(self, card_code: str):
            return SapCustomerRecord(card_code=card_code, card_name="Acme", price_list_num=3)

    class ItemAdapter:
        def get_item(self, item_code: str):
            return SapItemRecord(item_code=item_code, item_name="Widget", purchase_price=Decimal("10.00"))

    class PriceAdapter:
        def get_bp_price(self, card_code: str, item_code: str):
            return None

        def get_price_list_price(self, price_list_num: int, item_code: str):
            return Decimal("15.00")

    assert set_price(
        card_code="C10001",
        item_code="A0001",
        customer_repository=CustomerAdapter(),
        item_repository=ItemAdapter(),
        price_repository=PriceAdapter(),
    ) == Decimal("15.00")


def test_set_price_applies_purchase_price_floor_when_price_list_is_too_low():
    from ith_webapp.services.sap_pricing import set_price

    class CustomerAdapter:
        def get_customer(self, card_code: str):
            return SapCustomerRecord(card_code=card_code, card_name="Acme", price_list_num=3)

    class ItemAdapter:
        def get_item(self, item_code: str):
            return SapItemRecord(item_code=item_code, item_name="Widget", purchase_price=Decimal("10.00"))

    class PriceAdapter:
        def get_bp_price(self, card_code: str, item_code: str):
            return None

        def get_price_list_price(self, price_list_num: int, item_code: str):
            return Decimal("11.00")

    assert set_price(
        card_code="C10001",
        item_code="A0001",
        customer_repository=CustomerAdapter(),
        item_repository=ItemAdapter(),
        price_repository=PriceAdapter(),
    ) == Decimal("12.00")


def test_set_price_uses_lower_brazil_floor_for_customer_c007134():
    from ith_webapp.services.sap_pricing import set_price

    class CustomerAdapter:
        def get_customer(self, card_code: str):
            return SapCustomerRecord(card_code=card_code, card_name="Acme", price_list_num=3)

    class ItemAdapter:
        def get_item(self, item_code: str):
            return SapItemRecord(item_code=item_code, item_name="Widget", purchase_price=Decimal("10.00"))

    class PriceAdapter:
        def get_bp_price(self, card_code: str, item_code: str):
            return None

        def get_price_list_price(self, price_list_num: int, item_code: str):
            return Decimal("11.00")

    assert set_price(
        card_code="C007134",
        item_code="A0001",
        customer_repository=CustomerAdapter(),
        item_repository=ItemAdapter(),
        price_repository=PriceAdapter(),
    ) == Decimal("11.00")
