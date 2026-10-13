"""Route-level tests for the post endpoints (postRoutes)."""

from unittest import mock

from website import db
from website.models import RealtorAccount, User


def test_regex_flagged_post_returns_400_and_skips_claude(
    client, auth_headers, monkeypatch
):
    # Flagged title -> 400 before the Claude layer, so run_claude_checks is unused.
    spy = mock.Mock()
    monkeypatch.setattr("website.api.claudeModeration.run_claude_checks", spy)
    response = client.post(
        "/api/post",
        json={"title": "shit post", "description": "clean description"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    spy.assert_not_called()


def test_post_without_title_is_accepted(client, auth_headers):
    # Title is optional, so a missing key must not raise on the way in.
    response = client.post(
        "/api/post",
        json={"description": "a post with no title at all"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert client.get("/api/post").get_json()[0]["title"] == ""


def test_post_without_description_returns_400(client, auth_headers):
    response = client.post(
        "/api/post",
        json={"title": "just a title"},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_realtor_post_uses_realtor_claude_checks(
    client, auth_headers, userInfo, monkeypatch
):
    # A verified realtor's post should go through claudeRealtorModeration,
    # not the regular claudeModeration path.
    email, _ = userInfo
    user = User.query.filter_by(email=email).first()
    db.session.add(
        RealtorAccount(
            user_id=user.id,
            first_name="Test",
            last_name="Realtor",
            license_number="01234567",
            state="CA",
            city="Los Angeles",
            email=email,
            status="verified",
        )
    )
    db.session.commit()

    realtor_spy = mock.Mock(return_value=None)
    regular_spy = mock.Mock(return_value=None)
    monkeypatch.setattr(
        "website.api.claudeRealtorModeration.run_claude_checks", realtor_spy
    )
    monkeypatch.setattr("website.api.claudeModeration.run_claude_checks", regular_spy)

    response = client.post(
        "/api/post",
        json={"title": "Realtor post", "description": "A verified realtor's post"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    realtor_spy.assert_called_once()
    regular_spy.assert_not_called()


def test_feed_flags_posts_by_verified_agents(client, auth_headers, userInfo):
    email, _ = userInfo
    client.post(
        "/api/post",
        json={"title": "Agent post", "description": "From a verified agent"},
        headers=auth_headers,
    )
    # A second, regular user posts too.
    client.post(
        "/api/signup",
        json={
            "first_name": "Regular",
            "last_name": "User",
            "email": "regular@test.test",
            "password": "1234567893939393939",
        },
    )
    login = client.post(
        "/api/login",
        json={"email": "regular@test.test", "password": "1234567893939393939"},
    )
    regular = {"Authorization": f"Bearer {login.get_json()['access_token']}"}
    client.post(
        "/api/post",
        json={"title": "Regular post", "description": "From a regular user"},
        headers=regular,
    )

    agent = User.query.filter_by(email=email).first()
    for status in ("pending", "verified"):
        db.session.add(
            RealtorAccount(
                user_id=agent.id,
                first_name="Test",
                last_name="Agent",
                license_number="01234567",
                state="CA",
                city="Los Angeles",
                email=email,
                status=status,
            )
        )
        db.session.commit()
        flags = {
            p["title"]: p["author_is_agent"] for p in client.get("/api/post").get_json()
        }
        # Only a verified application earns the label; pending doesn't.
        assert flags == {
            "Agent post": status == "verified",
            "Regular post": False,
        }
        RealtorAccount.query.delete()
        db.session.commit()
