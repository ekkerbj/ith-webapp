from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class FinancialSummaryRow:
    industry: str
    item_code: str
    item_name: str
    salesperson: str
    state: str
    total: Decimal


def test_sap_financial_summary_report_renders_invoice_and_credit_memo_breakdowns(app):
    class FinancialSummaryRepository:
        def list_invoice_summaries(self):
            return [
                FinancialSummaryRow(
                    industry="Energy",
                    item_code="VALVE-1",
                    item_name="Valve",
                    salesperson="Jordan",
                    state="TX",
                    total=Decimal("125.50"),
                )
            ]

        def list_credit_memo_summaries(self):
            return [
                FinancialSummaryRow(
                    industry="Mining",
                    item_code="GAGE-9",
                    item_name="Gauge",
                    salesperson="Taylor",
                    state="AZ",
                    total=Decimal("75.00"),
                )
            ]

    app.config["SAP_FINANCIAL_SUMMARY_REPOSITORY"] = FinancialSummaryRepository()

    response = app.test_client().get("/reports/sap/financial-summaries")

    assert response.status_code == 200
    assert response.mimetype == "text/html"
    body = response.get_data(as_text=True)
    assert "SAP Financial Summaries" in body
    assert "Invoice Summaries" in body
    assert "Credit Memo Summaries" in body
    assert "Energy" in body
    assert "Valve" in body
    assert "Jordan" in body
    assert "TX" in body
    assert "Mining" in body
    assert "Gauge" in body
    assert "Taylor" in body
    assert "AZ" in body
