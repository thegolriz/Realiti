"""Tests for the post like and dislike routes."""


def test_like_post(client, auth_headers, post_id):
    response = client.post("/api/like", json={"postId": post_id}, headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["liked"] is True


def test_unlike_post(client, auth_headers, post_id):
    client.post("/api/like", json={"postId": post_id}, headers=auth_headers)
    response = client.post("/api/like", json={"postId": post_id}, headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["liked"] is False


def test_like_nonexistent_post(client, auth_headers):
    response = client.post("/api/like", json={"postId": 9999}, headers=auth_headers)
    assert response.status_code == 404


def test_like_no_auth(client, post_id):
    response = client.post("/api/like", json={"postId": post_id})
    assert response.status_code == 401


def test_dislike_post(client, auth_headers, post_id):
    response = client.post(
        "/api/dislike", json={"postId": post_id}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.get_json()["disliked"] is True


def test_undislike_post(client, auth_headers, post_id):
    client.post("/api/dislike", json={"postId": post_id}, headers=auth_headers)
    response = client.post(
        "/api/dislike", json={"postId": post_id}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.get_json()["disliked"] is False


def test_dislike_nonexistent_post(client, auth_headers):
    response = client.post("/api/dislike", json={"postId": 9999}, headers=auth_headers)
    assert response.status_code == 404


def test_dislike_no_auth(client, post_id):
    response = client.post("/api/dislike", json={"postId": post_id})
    assert response.status_code == 401
