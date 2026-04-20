from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class SapCustomerRecord:
    card_code: str
    card_name: str
    price_list_num: int | None = None


@dataclass(frozen=True, slots=True)
class SapItemRecord:
    item_code: str
    item_name: str
    purchase_price: Decimal | None = None


@dataclass(frozen=True, slots=True)
class SapInvoiceRecord:
    doc_entry: int
    doc_num: int
    card_code: str
    total: Decimal


@dataclass(frozen=True, slots=True)
class SapOrderRecord:
    doc_entry: int
    doc_num: int
    card_code: str
    total: Decimal


@dataclass(frozen=True, slots=True)
class SapWarehouseRecord:
    item_code: str
    warehouse_code: str
    min_stock: Decimal
    on_hand: Decimal
    committed: Decimal
    on_order: Decimal


@dataclass(frozen=True, slots=True)
class SapItemUsageRecord:
    item_code: str
    item_name: str
    credit_memo_qty: Decimal
    invoice_qty: Decimal
    production_qty: Decimal
    assembly_disassembly_qty: Decimal


@runtime_checkable
class SapCustomerRepository(Protocol):
    def get_customer(self, card_code: str) -> SapCustomerRecord | None:
        ...


@runtime_checkable
class SapItemRepository(Protocol):
    def get_item(self, item_code: str) -> SapItemRecord | None:
        ...


@runtime_checkable
class SapPriceRepository(Protocol):
    def get_bp_price(self, card_code: str, item_code: str) -> Decimal | None:
        ...

    def get_price_list_price(self, price_list_num: int, item_code: str) -> Decimal | None:
        ...


@runtime_checkable
class SapInvoiceRepository(Protocol):
    def get_invoice(self, doc_entry: int) -> SapInvoiceRecord | None:
        ...


@runtime_checkable
class SapOrderRepository(Protocol):
    def get_order(self, doc_entry: int) -> SapOrderRecord | None:
        ...


@runtime_checkable
class SapWarehouseRepository(Protocol):
    def get_stock(self, item_code: str, warehouse_code: str) -> SapWarehouseRecord | None:
        ...


@runtime_checkable
class SapItemUsageRepository(Protocol):
    def list_item_usage(self, period_years: int) -> list[SapItemUsageRecord]:
        ...
