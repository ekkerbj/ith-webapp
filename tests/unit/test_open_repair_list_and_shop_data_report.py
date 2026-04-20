from ith_webapp.models import CheckIn, CheckInSub, Customer, Service, ServiceTime


def test_open_repair_list_report_shows_unclosed_check_in_items(app):
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        customer = Customer(customer_name="Acme Service")
        session.add(customer)
        session.flush()

        check_in = CheckIn(customer_id=customer.customer_id, description="Open repair")
        session.add(check_in)
        session.flush()

        session.add_all(
            [
                CheckInSub(check_in_id=check_in.id, tool_id=101, inspected=True, closed=False),
                CheckInSub(check_in_id=check_in.id, tool_id=102, inspected=True, closed=True),
            ]
        )
        session.commit()

        response = app.test_client().get("/reports/check-in/open-repair-list")

        assert response.status_code == 200
        assert response.mimetype == "text/html"
        body = response.get_data(as_text=True)
        assert "Open Repair List" in body
        assert "Acme Service" in body
        assert "Tool 101" in body
        assert "Tool 102" not in body
    finally:
        session.close()


def test_shop_data_report_summarizes_service_workload(app):
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        customer = Customer(customer_name="Acme Service")
        session.add(customer)
        session.flush()

        service = Service(
            customer_id=customer.customer_id,
            technician="Tech One",
            order_status="Open",
            active=True,
        )
        session.add(service)
        session.flush()

        session.add(
            ServiceTime(
                service_id=service.service_id,
                technician="Tech One",
                hours=3.5,
                date="2026-04-19",
                labor_rate=95.0,
            )
        )
        session.commit()

        response = app.test_client().get("/reports/shop-data")

        assert response.status_code == 200
        assert response.mimetype == "text/html"
        body = response.get_data(as_text=True)
        assert "ITH Shop Data" in body
        assert "Tech One" in body
        assert "Open" in body
        assert "3.50" in body
    finally:
        session.close()
