import pytest


@pytest.fixture
def userInfo():
    email = "test@test.test"
    password = "12345678"
    return email, password
