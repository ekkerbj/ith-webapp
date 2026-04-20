def test_protected_route_redirects_to_login_when_not_authenticated(guest_client):
    response = guest_client.get("/customers/")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_login_post_stores_firebase_user_session_and_redirects(client, app):
    app.config["FIREBASE_AUTH_CLIENT"] = lambda email, password: {
        "email": email,
        "idToken": "token-123",
        "refreshToken": "refresh-123",
        "localId": "local-123",
        "role": "sales",
    }

    login_page = client.get("/login?next=/customers/")
    body = login_page.get_data(as_text=True)
    csrf_token = body.split('name="csrf_token" value="', 1)[1].split('"', 1)[0]

    response = client.post(
        "/login?next=/customers/",
        data={"email": "user@example.com", "password": "secret", "csrf_token": csrf_token},
    )

    assert response.status_code == 302
    assert "/customers/" in response.headers["Location"]
    with client.session_transaction() as session:
        assert session.get("firebase_user") == {
            "email": "user@example.com",
            "local_id": "local-123",
            "role": "sales",
        }


def test_readonly_user_cannot_open_customer_create_form(app):
    app.config["AUTH_REQUIRED"] = True
    app.config["FIREBASE_AUTH_CLIENT"] = lambda email, password: {
        "email": email,
        "idToken": "token-123",
        "refreshToken": "refresh-123",
        "role": "readonly",
    }
    client = app.test_client()
    login_page = client.get("/login?next=/customers/")
    csrf_token = login_page.get_data(as_text=True).split('name="csrf_token" value="', 1)[1].split('"', 1)[0]
    client.post(
        "/login?next=/customers/",
        data={"email": "user@example.com", "password": "secret", "csrf_token": csrf_token},
    )

    response = client.get("/customers/new")

    assert response.status_code == 403
