"""Shared pytest fixtures and test environment setup."""

import os

import pytest

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key")
os.environ.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")
# Claude client is constructed at import; a dummy key lets tests import
# claudeModeration without hitting the network.
os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")

from website import create_app, db  # noqa: E402


@pytest.fixture(autouse=True)
def _offline_claude(monkeypatch):
    # Neutralize the route's Claude call so post-creating tests stay offline
    # (no wasted API round-trips, no billing if a real key is in the env).
    # Tests that need to observe it can override this with their own patch.
    monkeypatch.setattr(
        "website.api.postRoutes.run_claude_checks", lambda *a, **k: None
    )


@pytest.fixture(autouse=True)
def _offline_hibp(monkeypatch):
    # Default every test's HIBP check to "clean" so signup-driven tests stay
    # offline (no network dependency, no HIBP rate limiting in CI). Tests
    # that need to exercise the compromised/unknown branches override this
    # with their own patch.
    monkeypatch.setattr("website.api.auth_routes.hashMode", lambda password: "clean")


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
    return "test@test.test", "123456789293829"


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
