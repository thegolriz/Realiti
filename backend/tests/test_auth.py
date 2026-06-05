def test_signup(client, userInfo):
    email, password = userInfo
    user = {
        "first_name": "tester1",
        "last_name": "snondw",
        "email": email,
        "password": password,
    }
    response = client.post("/api/signup", json=user)
    assert response.status_code == 201
    assert response.get_json()["message"] == "account created"


def test_login(client, userInfo):
    email, password = userInfo
    client.post(
        "/api/signup",
        json={
            "first_name": "tester1",
            "last_name": "snondw",
            "email": email,
            "password": password,
        },
    )
    response = client.post("/api/login", json={"email": email, "password": password})
    assert response.status_code == 200
    assert "access_token" in response.get_json()
