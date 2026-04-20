from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ItemUsageRow:
    item_code: str
    item_name: str
    credit_memo_qty: Decimal
    invoice_qty: Decimal
    production_qty: Decimal
    assembly_disassembly_qty: Decimal


def test_sap_item_usage_report_renders_one_two_and_three_year_sections(app):
    class ItemUsageRepository:
        def __init__(self):
            self.periods = []

        def list_item_usage(self, period_years: int):
            self.periods.append(period_years)
            rows = {
                1: [
                    ItemUsageRow(
                        item_code="VALVE-1",
                        item_name="Valve",
                        credit_memo_qty=Decimal("1"),
                        invoice_qty=Decimal("5"),
                        production_qty=Decimal("2"),
                        assembly_disassembly_qty=Decimal("0"),
                    )
                ],
                2: [
                    ItemUsageRow(
                        item_code="GAGE-9",
                        item_name="Gauge",
                        credit_memo_qty=Decimal("2"),
                        invoice_qty=Decimal("8"),
                        production_qty=Decimal("4"),
                        assembly_disassembly_qty=Decimal("1"),
                    )
                ],
                3: [
                    ItemUsageRow(
                        item_code="MTR-7",
                        item_name="Motor",
                        credit_memo_qty=Decimal("3"),
                        invoice_qty=Decimal("9"),
                        production_qty=Decimal("6"),
                        assembly_disassembly_qty=Decimal("2"),
                    )
                ],
            }
            return rows[period_years]

    repository = ItemUsageRepository()
    app.config["SAP_ITEM_USAGE_REPOSITORY"] = repository

    response = app.test_client().get("/reports/sap/item-usage")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Item Usage Analytics" in body
    assert "1 Year" in body
    assert "2 Years" in body
    assert "3 Years" in body
    assert "VALVE-1" in body
    assert "GAGE-9" in body
    assert "MTR-7" in body
    assert repository.periods == [1, 2, 3]
