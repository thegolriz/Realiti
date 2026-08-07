"""Tests for the admin dashboard (review queue + reports) and reporting."""

from website import db
from website.api.claudeModeration import DECISION_REVIEW, Verdict
from website.models import User

REVIEW_VERDICT = Verdict(DECISION_REVIEW, "unsure")


def _make_admin(client, email="admin@test.test", password="12345678"):
    client.post(
        "/api/signup",
        json={
            "first_name": "Admin",
            "last_name": "User",
            "email": email,
            "password": password,
        },
    )
    user = User.query.filter_by(email=email).first()
    user.is_admin = True
    db.session.commit()
    login = client.post("/api/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {login.get_json()['access_token']}"}


def _force_review(monkeypatch):
    monkeypatch.setattr(
        "website.api.postRoutes.run_claude_checks",
        lambda *a, **k: REVIEW_VERDICT,
    )


def test_admin_routes_reject_non_admin(client, auth_headers):
    resp = client.get("/api/admin/review-posts", headers=auth_headers)
    assert resp.status_code == 403


def test_admin_routes_reject_anonymous(client):
    resp = client.get("/api/admin/review-posts")
    assert resp.status_code == 401


def test_needs_review_post_hidden_then_approved(client, auth_headers, monkeypatch):
    _force_review(monkeypatch)
    resp = client.post(
        "/api/post",
        json={"title": "Maybe", "description": "borderline content"},
        headers=auth_headers,
    )
    assert resp.status_code == 202

    # Hidden from the public feed.
    assert client.get("/api/post").get_json() == []

    # Visible in the admin queue with the reviewer's context.
    admin = _make_admin(client)
    queue = client.get("/api/admin/review-posts", headers=admin).get_json()
    assert len(queue) == 1
    assert queue[0]["review_reason"] == "unsure"
    post_id = queue[0]["id"]

    # Approve -> shows in the feed, leaves the queue.
    approve = client.post(f"/api/admin/review-posts/{post_id}/approve", headers=admin)
    assert approve.status_code == 200
    assert len(client.get("/api/post").get_json()) == 1
    assert client.get("/api/admin/review-posts", headers=admin).get_json() == []


def test_needs_review_post_rejected_stays_hidden(client, auth_headers, monkeypatch):
    _force_review(monkeypatch)
    client.post(
        "/api/post",
        json={"title": "Maybe", "description": "borderline"},
        headers=auth_headers,
    )
    admin = _make_admin(client)
    queue = client.get("/api/admin/review-posts", headers=admin).get_json()
    post_id = queue[0]["id"]
    client.post(f"/api/admin/review-posts/{post_id}/reject", headers=admin)
    assert client.get("/api/post").get_json() == []
    assert client.get("/api/admin/review-posts", headers=admin).get_json() == []


def test_report_creation_and_uphold(client, auth_headers, post_id):
    resp = client.post(
        "/api/report",
        json={"postId": post_id, "reason": "spam", "evidence_url": "http://x/y"},
        headers=auth_headers,
    )
    assert resp.status_code == 201

    admin = _make_admin(client)
    reports = client.get("/api/admin/reports", headers=admin).get_json()
    assert len(reports) == 1
    assert reports[0]["post"]["id"] == post_id
    report_id = reports[0]["id"]

    # Uphold -> post drops out of the feed, report leaves the open list.
    resolve = client.post(
        f"/api/admin/reports/{report_id}/resolve",
        json={"action": "uphold"},
        headers=admin,
    )
    assert resolve.status_code == 200
    assert client.get("/api/post").get_json() == []
    assert client.get("/api/admin/reports", headers=admin).get_json() == []


def test_report_dismiss_keeps_post(client, auth_headers, post_id):
    client.post(
        "/api/report",
        json={"postId": post_id, "reason": "spam"},
        headers=auth_headers,
    )
    admin = _make_admin(client)
    report_id = client.get("/api/admin/reports", headers=admin).get_json()[0]["id"]
    client.post(
        f"/api/admin/reports/{report_id}/resolve",
        json={"action": "dismiss"},
        headers=admin,
    )
    assert len(client.get("/api/post").get_json()) == 1
    assert client.get("/api/admin/reports", headers=admin).get_json() == []


def test_report_requires_reason(client, auth_headers, post_id):
    resp = client.post("/api/report", json={"postId": post_id}, headers=auth_headers)
    assert resp.status_code == 400
