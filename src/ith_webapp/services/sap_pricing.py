from __future__ import annotations

from decimal import Decimal

from ith_webapp.repositories.sap_repository import (
    SapCustomerRepository,
    SapItemRepository,
    SapPriceRepository,
)


def set_price(
    *,
    card_code: str,
    item_code: str,
    customer_repository: SapCustomerRepository,
    item_repository: SapItemRepository,
    price_repository: SapPriceRepository,
) -> Decimal:
    bp_price = price_repository.get_bp_price(card_code, item_code)
    if bp_price is not None:
        return bp_price

    customer = customer_repository.get_customer(card_code)
    if customer is None:
        raise ValueError(f"Customer not found: {card_code}")

    item = item_repository.get_item(item_code)
    if item is None or item.purchase_price is None:
        raise ValueError(f"Item purchase price not found: {item_code}")

    price_list_price = None
    if customer.price_list_num is not None:
        price_list_price = price_repository.get_price_list_price(customer.price_list_num, item_code)

    floor_multiplier = Decimal("1.1") if card_code == "C007134" else Decimal("1.2")
    floor_price = item.purchase_price * floor_multiplier
    if price_list_price is None:
        return floor_price
    return max(price_list_price, floor_price)
