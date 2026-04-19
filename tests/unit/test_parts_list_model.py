import pytest
from ith_webapp.models.part import Part
# RED: F-026 Parts List / Bill of Materials
# This test will fail until the PartsList and PartsSub models are implemented.

def test_parts_list_and_sub_fields():
    # Attempt to import (should fail RED)
    from ith_webapp.models.parts_list import PartsList, PartsSub
    pl = PartsList(name="Assembly 1")
    sub = PartsSub(parts_list_id=1, part_id=2, quantity=3)
    assert pl.name == "Assembly 1"
    assert sub.parts_list_id == 1
    assert sub.part_id == 2
    assert sub.quantity == 3
