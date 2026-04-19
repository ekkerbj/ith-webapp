import pytest
from ith_webapp.models.part import Part

def test_part_model_fields():
    part = Part(
        part_id=1,
        part_number="P-1001",
        description="Test Part",
        active=True
    )
    assert part.part_id == 1
    assert part.part_number == "P-1001"
    assert part.description == "Test Part"
    assert part.active is True
