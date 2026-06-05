def _signup_payload(email, password):
    return {
        "first_name": "Test",
        "last_name": "User",
        "email": email,
        "password": password,
    }


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
    assert "refresh_token" in body


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
