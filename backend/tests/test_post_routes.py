"""Route-level tests for the post endpoints (postRoutes)."""

from unittest import mock

from website import db
from website.models import Realtor, User


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
        Realtor(name="Test Realtor", state="CA", is_verified=True, user_id=user.id)
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
