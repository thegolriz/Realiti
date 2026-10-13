"""Tests for the real estate agent verification apply and confirm routes."""

import time
from urllib.parse import parse_qs, urlparse

from itsdangerous import TimestampSigner

from website import db
from website.api.realtorRoutes import _confirm_serializer
from website.models import RealtorAccount

URL = "/api/send_verification"
CONFIRM_URL = "/api/realtor/confirm"


def _application(**overrides):
    # Matches the auth_headers user from conftest.
    body = {
        "email": "test@test.test",
        "first_name": "Tester",
        "last_name": "User",
        "license_number": "sl3456789",
        "state": "fl",
        "city": "Miami",
    }
    body.update(overrides)
    return body


def _second_user(client, email="other@test.test", password="1234567893939393939"):
    client.post(
        "/api/signup",
        json={
            "first_name": "Other",
            "last_name": "Agent",
            "email": email,
            "password": password,
        },
    )
    login = client.post("/api/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {login.get_json()['access_token']}"}


def test_apply_requires_login(client):
    resp = client.post(URL, json=_application())
    assert resp.status_code == 401


def test_apply_creates_pending_application(client, auth_headers):
    resp = client.post(URL, json=_application(city="  Miami  "), headers=auth_headers)
    assert resp.status_code == 201

    row = RealtorAccount.query.one()
    assert row.status == "email_pending"
    assert row.license_number == "SL3456789"
    assert row.state == "FL"
    assert row.city == "Miami"
    assert row.email == "test@test.test"
    assert row.submitted_at is not None
    assert row.email_confirmed_at is None


def test_apply_email_match_ignores_case_and_spaces(client, auth_headers):
    resp = client.post(
        URL, json=_application(email="  TEST@Test.test "), headers=auth_headers
    )
    assert resp.status_code == 201


def test_apply_rejects_other_email(client, auth_headers):
    resp = client.post(
        URL, json=_application(email="someone@else.com"), headers=auth_headers
    )
    assert resp.status_code == 403
    assert RealtorAccount.query.count() == 0


def test_apply_rejects_missing_field(client, auth_headers):
    body = _application()
    del body["city"]
    resp = client.post(URL, json=body, headers=auth_headers)
    assert resp.status_code == 400


def test_apply_rejects_blank_field(client, auth_headers):
    resp = client.post(URL, json=_application(city="   "), headers=auth_headers)
    assert resp.status_code == 400


def test_apply_rejects_non_string_field(client, auth_headers):
    resp = client.post(URL, json=_application(license_number=123), headers=auth_headers)
    assert resp.status_code == 400


def test_apply_rejects_empty_body(client, auth_headers):
    resp = client.post(URL, json={}, headers=auth_headers)
    assert resp.status_code == 400


def test_apply_rejects_long_license(client, auth_headers):
    resp = client.post(
        URL, json=_application(license_number="A" * 31), headers=auth_headers
    )
    assert resp.status_code == 400
    assert RealtorAccount.query.count() == 0


def test_apply_blocks_second_active_application(client, auth_headers):
    client.post(URL, json=_application(), headers=auth_headers)
    resp = client.post(URL, json=_application(), headers=auth_headers)
    assert resp.status_code == 409
    assert RealtorAccount.query.count() == 1


def test_apply_allowed_after_rejection(client, auth_headers):
    client.post(URL, json=_application(), headers=auth_headers)
    RealtorAccount.query.one().status = "rejected"
    db.session.commit()

    resp = client.post(URL, json=_application(), headers=auth_headers)
    assert resp.status_code == 201
    assert RealtorAccount.query.count() == 2


def test_apply_blocks_license_verified_elsewhere(client, auth_headers):
    client.post(URL, json=_application(), headers=auth_headers)
    RealtorAccount.query.one().status = "verified"
    db.session.commit()

    other = _second_user(client)
    resp = client.post(URL, json=_application(email="other@test.test"), headers=other)
    assert resp.status_code == 409


def test_apply_pending_license_does_not_block_others(client, auth_headers):
    # An impostor's unverified application must not lock out the real agent.
    client.post(URL, json=_application(), headers=auth_headers)

    other = _second_user(client)
    resp = client.post(URL, json=_application(email="other@test.test"), headers=other)
    assert resp.status_code == 201


def test_apply_sends_confirmation_email(client, auth_headers, monkeypatch):
    sent = []
    monkeypatch.setattr(
        "website.api.realtorRoutes.send_verification_email",
        lambda to, link: sent.append((to, link)) or True,
    )
    resp = client.post(URL, json=_application(), headers=auth_headers)
    assert resp.status_code == 201
    assert "warning" not in resp.get_json()

    to, link = sent[0]
    assert to == "test@test.test"
    assert "/realtor-verify/confirm?token=" in link


def test_apply_failed_email_still_saves_with_warning(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "website.api.realtorRoutes.send_verification_email", lambda *a, **k: False
    )
    resp = client.post(URL, json=_application(), headers=auth_headers)
    assert resp.status_code == 201
    assert "warning" in resp.get_json()
    assert RealtorAccount.query.one().status == "email_pending"


def _apply_and_get_token(client, auth_headers, monkeypatch):
    # Apply for real and pull the token out of the link the route emailed.
    sent = []
    monkeypatch.setattr(
        "website.api.realtorRoutes.send_verification_email",
        lambda to, link: sent.append(link) or True,
    )
    client.post(URL, json=_application(), headers=auth_headers)
    return parse_qs(urlparse(sent[0]).query)["token"][0]


def test_confirm_moves_application_to_pending(client, auth_headers, monkeypatch):
    token = _apply_and_get_token(client, auth_headers, monkeypatch)
    resp = client.post(CONFIRM_URL, json={"token": token})
    assert resp.status_code == 200

    row = RealtorAccount.query.one()
    assert row.status == "pending"
    assert row.email_confirmed_at is not None


def test_confirm_needs_no_login(client, auth_headers, monkeypatch):
    # The link may be opened on a device that isn't signed in.
    token = _apply_and_get_token(client, auth_headers, monkeypatch)
    resp = client.post(CONFIRM_URL, json={"token": token}, headers={})
    assert resp.status_code == 200


def test_confirm_twice_is_not_an_error(client, auth_headers, monkeypatch):
    token = _apply_and_get_token(client, auth_headers, monkeypatch)
    client.post(CONFIRM_URL, json={"token": token})
    first_confirmed_at = RealtorAccount.query.one().email_confirmed_at

    resp = client.post(CONFIRM_URL, json={"token": token})
    assert resp.status_code == 200
    row = RealtorAccount.query.one()
    assert row.status == "pending"
    assert row.email_confirmed_at == first_confirmed_at


def test_confirm_rejects_missing_token(client):
    assert client.post(CONFIRM_URL, json={}).status_code == 400
    assert client.post(CONFIRM_URL).status_code == 400


def test_confirm_rejects_garbage_token(client):
    resp = client.post(CONFIRM_URL, json={"token": "not-a-real-token"})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "This link is invalid."


def test_confirm_rejects_tampered_token(client, auth_headers, monkeypatch):
    token = _apply_and_get_token(client, auth_headers, monkeypatch)
    resp = client.post(CONFIRM_URL, json={"token": token[:-2] + "xx"})
    assert resp.status_code == 400
    assert RealtorAccount.query.one().status == "email_pending"


def test_confirm_rejects_expired_token(client, auth_headers, monkeypatch):
    _apply_and_get_token(client, auth_headers, monkeypatch)
    application = RealtorAccount.query.one()
    # Sign the token 25 hours in the past, past the route's 24 hour max_age.
    with monkeypatch.context() as m:
        m.setattr(
            TimestampSigner, "get_timestamp", lambda self: int(time.time()) - 90000
        )
        token = _confirm_serializer().dumps(
            {"application_id": application.id, "email": application.email}
        )

    resp = client.post(CONFIRM_URL, json={"token": token})
    assert resp.status_code == 400
    assert "expired" in resp.get_json()["error"]
    assert RealtorAccount.query.one().status == "email_pending"


def test_confirm_rejects_rejected_application(client, auth_headers, monkeypatch):
    token = _apply_and_get_token(client, auth_headers, monkeypatch)
    RealtorAccount.query.one().status = "rejected"
    db.session.commit()

    resp = client.post(CONFIRM_URL, json={"token": token})
    assert resp.status_code == 400
    assert RealtorAccount.query.one().status == "rejected"


def test_confirm_already_verified(client, auth_headers, monkeypatch):
    token = _apply_and_get_token(client, auth_headers, monkeypatch)
    RealtorAccount.query.one().status = "verified"
    db.session.commit()

    resp = client.post(CONFIRM_URL, json={"token": token})
    assert resp.status_code == 200
    assert RealtorAccount.query.one().status == "verified"


def test_confirm_deleted_application(client, auth_headers, monkeypatch):
    token = _apply_and_get_token(client, auth_headers, monkeypatch)
    db.session.delete(RealtorAccount.query.one())
    db.session.commit()

    resp = client.post(CONFIRM_URL, json={"token": token})
    assert resp.status_code == 404


def test_confirm_rejects_token_for_changed_email(client, auth_headers, monkeypatch):
    token = _apply_and_get_token(client, auth_headers, monkeypatch)
    RealtorAccount.query.one().email = "changed@test.test"
    db.session.commit()

    resp = client.post(CONFIRM_URL, json={"token": token})
    assert resp.status_code == 400
    assert RealtorAccount.query.one().status == "email_pending"
