import os

import pytest

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key")
os.environ.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")

from website import create_app, db  # noqa: E402


@pytest.fixture
def app(tmp_path):
    os.environ["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{tmp_path / 'test.db'}"
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def userInfo():
    return "test@test.test", "12345678"


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
