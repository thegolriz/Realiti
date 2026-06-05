import os

import pytest
from sqlalchemy.pool import StaticPool


@pytest.fixture
def app():
    os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    os.environ["SECRET_KEY"] = "test-secret"
    os.environ["JWT_SECRET_KEY"] = "test-secret"

    from website import create_app, db

    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def userInfo():
    email = "test@test.test"
    password = "12345678"
    return email, password


@pytest.fixture
def auth_headers(client, userInfo):
    email, password = userInfo
    client.post(
        "/api/signup",
        json={
            "first_name": "Tester",
            "last_name": "User",
            "email": email,
            "password": password,
        },
    )
    response = client.post("/api/login", json={"email": email, "password": password})
    token = response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def post_id(client, auth_headers):
    client.post(
        "/api/post",
        json={
            "title": "Test Post",
            "description": "A test post",
        },
        headers=auth_headers,
    )
    posts = client.get("/api/post").get_json()
    return posts[0]["id"]
