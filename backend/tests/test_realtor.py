"""Tests for the real estate agent verification apply route."""

from website import db
from website.models import RealtorAccount

URL = "/api/send_verification"


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
