import pytest

def test_signup(client,userInfo):
    email, password = userInfo
    user = {
        "firstname":"tester1",
        "lastname":"snondw",
        "email":email,
        "password": password
    }
    response = client.post("/signup",json = user)
    assert response.status_code == 200
    assert response.get_json()["message"] == "account created"

    
