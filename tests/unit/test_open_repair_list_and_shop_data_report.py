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


def test_repair_time_analysis_report_groups_time_by_service_and_technician(app):
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        customer = Customer(customer_name="Acme Repair")
        session.add(customer)
        session.flush()

        service_one = Service(
            customer_id=customer.customer_id,
            technician="Tech One",
            order_status="Open",
            active=True,
        )
        service_two = Service(
            customer_id=customer.customer_id,
            technician="Tech Two",
            order_status="Closed",
            active=True,
        )
        session.add_all([service_one, service_two])
        session.flush()

        session.add_all(
            [
                ServiceTime(
                    service_id=service_one.service_id,
                    technician="Tech One",
                    hours=1.5,
                    date="2026-04-18",
                    labor_rate=100.0,
                ),
                ServiceTime(
                    service_id=service_one.service_id,
                    technician="Tech One",
                    hours=2.0,
                    date="2026-04-19",
                    labor_rate=100.0,
                ),
                ServiceTime(
                    service_id=service_two.service_id,
                    technician="Tech Two",
                    hours=0.5,
                    date="2026-04-19",
                    labor_rate=150.0,
                ),
            ]
        )
        session.commit()

        response = app.test_client().get("/reports/repair-time-analysis")

        assert response.status_code == 200
        assert response.mimetype == "text/html"
        body = response.get_data(as_text=True)
        assert "Repair Time Analysis" in body
        assert "Acme Repair" in body
        assert "Tech One" in body
        assert "3.50" in body
        assert "Tech Two" in body
        assert "0.50" in body
    finally:
        session.close()
