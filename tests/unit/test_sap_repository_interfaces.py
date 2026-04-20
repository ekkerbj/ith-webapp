from decimal import Decimal

from ith_webapp.repositories.sap_repository import (
    SapCustomerRecord,
    SapCustomerRepository,
    SapInvoiceRecord,
    SapInvoiceRepository,
    SapItemUsageRecord,
    SapItemRecord,
    SapItemRepository,
    SapOrderRecord,
    SapOrderRepository,
    SapPriceRepository,
    SapItemUsageRepository,
    SapWarehouseRecord,
    SapWarehouseRepository,
)


def test_customer_repository_protocol_accepts_matching_adapter():
    class CustomerAdapter:
        def get_customer(self, card_code: str):
            return SapCustomerRecord(card_code=card_code, card_name="Acme", price_list_num=1)

    assert isinstance(CustomerAdapter(), SapCustomerRepository)


def test_item_repository_protocol_accepts_matching_adapter():
    class ItemAdapter:
        def get_item(self, item_code: str):
            return SapItemRecord(item_code=item_code, item_name="Widget", purchase_price=Decimal("10.00"))

    assert isinstance(ItemAdapter(), SapItemRepository)


def test_price_repository_protocol_accepts_matching_adapter():
    class PriceAdapter:
        def get_bp_price(self, card_code: str, item_code: str):
            return Decimal("12.34")

        def get_price_list_price(self, price_list_num: int, item_code: str):
            return Decimal("11.11")

    assert isinstance(PriceAdapter(), SapPriceRepository)


def test_invoice_repository_protocol_accepts_matching_adapter():
    class InvoiceAdapter:
        def get_invoice(self, doc_entry: int):
            return SapInvoiceRecord(doc_entry=doc_entry, doc_num=1001, card_code="C10001", total=Decimal("99.99"))

    assert isinstance(InvoiceAdapter(), SapInvoiceRepository)


def test_order_repository_protocol_accepts_matching_adapter():
    class OrderAdapter:
        def get_order(self, doc_entry: int):
            return SapOrderRecord(doc_entry=doc_entry, doc_num=2001, card_code="C10001", total=Decimal("49.99"))

    assert isinstance(OrderAdapter(), SapOrderRepository)


def test_warehouse_repository_protocol_accepts_matching_adapter():
    class WarehouseAdapter:
        def get_stock(self, item_code: str, warehouse_code: str):
            return SapWarehouseRecord(
                item_code=item_code,
                warehouse_code=warehouse_code,
                min_stock=Decimal("5"),
                on_hand=Decimal("10"),
                committed=Decimal("2"),
                on_order=Decimal("1"),
            )

    assert isinstance(WarehouseAdapter(), SapWarehouseRepository)


def test_item_usage_repository_protocol_accepts_matching_adapter():
    class ItemUsageAdapter:
        def list_item_usage(self, period_years: int):
            return [
                SapItemUsageRecord(
                    item_code=f"ITEM-{period_years}",
                    item_name="Widget",
                    credit_memo_qty=Decimal("1"),
                    invoice_qty=Decimal("2"),
                    production_qty=Decimal("3"),
                    assembly_disassembly_qty=Decimal("4"),
                )
            ]

    assert isinstance(ItemUsageAdapter(), SapItemUsageRepository)
