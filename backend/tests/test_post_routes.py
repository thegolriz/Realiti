"""Route-level tests for the post endpoints (postRoutes)."""

from unittest import mock


def test_regex_flagged_post_returns_400_and_skips_claude(
    client, auth_headers, monkeypatch
):
    # Flagged title -> 400 before the Claude layer, so run_claude_checks is unused.
    spy = mock.Mock()
    monkeypatch.setattr("website.api.postRoutes.run_claude_checks", spy)
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
