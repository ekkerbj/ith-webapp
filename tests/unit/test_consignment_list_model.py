def test_consignment_list_fields():
    from ith_webapp.models.consignment_list import ConsignmentList

    consignment = ConsignmentList(
        customer_id=1,
        part_id=1,
        quantity=12,
    )

    assert consignment.customer_id == 1
    assert consignment.part_id == 1
    assert consignment.quantity == 12
