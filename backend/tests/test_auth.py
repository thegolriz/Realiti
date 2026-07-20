"""Tests for the auth routes: signup, login, refresh, and logout."""


def _signup_payload(email, password):
    return {
        "first_name": "Test",
        "last_name": "User",
        "email": email,
        "password": password,
    }


def _cookie_value(response, name):
    """Pull a cookie's value out of a response's Set-Cookie headers."""
    for header in response.headers.getlist("Set-Cookie"):
        if header.startswith(name + "="):
            return header.split(";", 1)[0].split("=", 1)[1]
    return None


def test_signup_success(client, userInfo):
    email, password = userInfo
    response = client.post("/api/signup", json=_signup_payload(email, password))
    assert response.status_code == 201
    assert response.get_json()["message"] == "account created"


def test_signup_missing_fields(client):
    response = client.post("/api/signup", json={"email": "x@x.x"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing required fields"


def test_signup_no_body(client):
    response = client.post("/api/signup", json={})
    assert response.status_code == 400


def test_signup_short_password(client, userInfo):
    email, _ = userInfo
    response = client.post("/api/signup", json=_signup_payload(email, "short"))
    assert response.status_code == 400
    assert "at least 8 characters" in response.get_json()["error"]


def test_signup_duplicate_email(client, userInfo):
    email, password = userInfo
    payload = _signup_payload(email, password)
    client.post("/api/signup", json=payload)
    response = client.post("/api/signup", json=payload)
    assert response.status_code == 400
    assert response.get_json()["error"] == "email in use"


def test_login_success(client, userInfo):
    email, password = userInfo
    client.post("/api/signup", json=_signup_payload(email, password))

    response = client.post("/api/login", json={"email": email, "password": password})
    assert response.status_code == 200
    body = response.get_json()
    assert "access_token" in body
    # The refresh token is delivered as an httpOnly cookie now, not in the
    # body, so JS can never read it.
    assert "refresh_token" not in body
    assert _cookie_value(response, "refresh_token_cookie")


def test_refresh_and_logout_flow(client, userInfo):
    email, password = userInfo
    client.post("/api/signup", json=_signup_payload(email, password))
    login = client.post("/api/login", json={"email": email, "password": password})
    csrf = _cookie_value(login, "csrf_refresh_token")
    assert csrf

    # The refresh cookie (auto-sent by the test client) mints a new access
    # token when the CSRF token is echoed back.
    refreshed = client.post("/api/refresh", headers={"X-CSRF-TOKEN": csrf})
    assert refreshed.status_code == 200
    new_access = refreshed.get_json()["access_token"]
    assert new_access

    # That fresh access token is accepted on a protected route.
    protected = client.get(
        "/api/protected", headers={"Authorization": f"Bearer {new_access}"}
    )
    assert protected.status_code == 200

    # Logout clears the refresh cookie, so a later refresh is rejected.
    logout = client.post("/api/logout")
    assert logout.status_code == 200
    after = client.post("/api/refresh", headers={"X-CSRF-TOKEN": csrf})
    assert after.status_code in (401, 422)


def test_login_missing_fields(client):
    response = client.post("/api/login", json={"email": "x@x.x"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing email and/or password"


def test_login_no_body(client):
    response = client.post("/api/login", json={})
    assert response.status_code == 400


def test_login_wrong_password(client, userInfo):
    email, password = userInfo
    client.post("/api/signup", json=_signup_payload(email, password))

    response = client.post(
        "/api/login", json={"email": email, "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid email or password"


def test_login_nonexistent_user(client, userInfo):
    email, password = userInfo
    response = client.post("/api/login", json={"email": email, "password": password})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid email or password"
