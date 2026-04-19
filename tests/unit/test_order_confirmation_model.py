def test_order_confirmation_fields():
    from ith_webapp.models.order_confirmation import OrderConfirmation

    confirmation = OrderConfirmation(
        customer_id=1,
        order_number="OC-1001",
        notes="Confirmed by phone",
    )

    assert confirmation.customer_id == 1
    assert confirmation.order_number == "OC-1001"
    assert confirmation.notes == "Confirmed by phone"
