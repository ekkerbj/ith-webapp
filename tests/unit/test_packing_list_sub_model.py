import pytest
from ith_webapp.models.packing_list_sub import PackingListSub

def test_packing_list_sub_fields():
    sub = PackingListSub(
        packing_list_id=1,
        harm_number="1234",
        EECN="EECN1",
        DDTC="DDTC1",
        COO="USA",
        in_bond_code="BOND1"
    )
    assert sub.packing_list_id == 1
    assert sub.harm_number == "1234"
    assert sub.EECN == "EECN1"
    assert sub.DDTC == "DDTC1"
    assert sub.COO == "USA"
    assert sub.in_bond_code == "BOND1"
