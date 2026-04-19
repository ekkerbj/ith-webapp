# RED: F-027 Parts Sold History
# This test will fail until the PartsSold model is implemented.


def test_parts_sold_fields():
    from ith_webapp.models.parts_sold import PartsSold
    ps = PartsSold(part_id=1, quantity=5, sold_date="2024-01-01")
    assert ps.part_id == 1
    assert ps.quantity == 5
    assert ps.sold_date == "2024-01-01"
