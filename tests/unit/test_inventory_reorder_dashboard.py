from decimal import Decimal

from ith_webapp.app import create_app
from ith_webapp.repositories.sap_repository import SapWarehouseRecord


def test_inventory_reorder_dashboard_lists_only_items_needing_reorder():
    app = create_app(testing=True)

    class WarehouseRepository:
        def get_stock(self, item_code: str, warehouse_code: str):
            records = {
                "A100": SapWarehouseRecord(
                    item_code="A100",
                    warehouse_code=warehouse_code,
                    min_stock=Decimal("10"),
                    on_hand=Decimal("4"),
                    committed=Decimal("3"),
                    on_order=Decimal("1"),
                ),
                "B200": SapWarehouseRecord(
                    item_code="B200",
                    warehouse_code=warehouse_code,
                    min_stock=Decimal("5"),
                    on_hand=Decimal("10"),
                    committed=Decimal("0"),
                    on_order=Decimal("0"),
                ),
            }
            return records.get(item_code)

    app.config["INVENTORY_REORDER_REPOSITORY"] = WarehouseRepository()
    app.config["INVENTORY_REORDER_WAREHOUSE_CODE"] = "MAIN"
    app.config["INVENTORY_REORDER_ITEM_CODES"] = ["A100", "B200"]

    client = app.test_client()
    response = client.get("/inventory/reorder")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "A100" in html
    assert "8" in html
    assert "B200" not in html
