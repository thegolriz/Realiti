"""Malformed request bodies return the app's JSON error shape, not HTML."""


def test_malformed_json_body_returns_400_json(client):
    # Valid JSON content type, broken body -> werkzeug BadRequest -> our JSON.
    resp = client.post(
        "/api/login", data="not json", content_type="application/json"
    )
    assert resp.status_code == 400
    assert resp.get_json()["error"]


def test_non_json_content_type_returns_415_json(client):
    resp = client.post("/api/login", data="hello", content_type="text/plain")
    assert resp.status_code == 415
    assert resp.get_json()["error"]
