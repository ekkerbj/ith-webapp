def test_protected_route_redirects_to_login_when_not_authenticated(guest_client):
    response = guest_client.get("/customers/")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_login_post_stores_firebase_user_session_and_redirects(client, app):
    app.config["FIREBASE_AUTH_CLIENT"] = lambda email, password: {
        "email": email,
        "idToken": "token-123",
        "refreshToken": "refresh-123",
    }

    response = client.post(
        "/login?next=/customers/",
        data={"email": "user@example.com", "password": "secret"},
    )

    assert response.status_code == 302
    assert "/customers/" in response.headers["Location"]
    with client.session_transaction() as session:
        assert session.get("firebase_user") is not None
