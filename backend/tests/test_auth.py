"""Tests for the auth routes: signup, login, refresh, and logout."""

from website import db
from website.models import Post, PostDislikes, PostLikes, Replies, User


def _signup_payload(email, password):
    return {
        "first_name": "Test",
        "last_name": "User",
        "email": email,
        "password": password,
    }


def _cookie_value(response, name):
    """Pull a cookie's value out of a response's Set-Cookie headers."""
    for header in response.headers.getlist("Set-Cookie"):
        if header.startswith(name + "="):
            return header.split(";", 1)[0].split("=", 1)[1]
    return None


def test_signup_success(client, userInfo):
    email, password = userInfo
    response = client.post(
        "/api/signup", json=_signup_payload(email, password))
    assert response.status_code == 201
    assert response.get_json()["message"] == "account created"


def test_signup_missing_fields(client):
    response = client.post("/api/signup", json={"email": "x@x.x"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing required fields"


def test_signup_no_body(client):
    response = client.post("/api/signup", json={})
    assert response.status_code == 400


def test_signup_short_password(client, userInfo):
    email, _ = userInfo
    response = client.post("/api/signup", json=_signup_payload(email, "short"))
    assert response.status_code == 400
    assert "at least 8 characters" in response.get_json()["error"]


def test_signup_duplicate_email(client, userInfo):
    email, password = userInfo
    payload = _signup_payload(email, password)
    client.post("/api/signup", json=payload)
    response = client.post("/api/signup", json=payload)
    assert response.status_code == 400
    assert response.get_json()["error"] == "email in use"


def test_login_success(client, userInfo):
    email, password = userInfo
    client.post("/api/signup", json=_signup_payload(email, password))

    response = client.post(
        "/api/login", json={"email": email, "password": password})
    assert response.status_code == 200
    body = response.get_json()
    assert "access_token" in body
    assert "refresh_token" not in body
    assert _cookie_value(response, "refresh_token_cookie")


def test_refresh_and_logout_flow(client, userInfo):
    email, password = userInfo
    client.post("/api/signup", json=_signup_payload(email, password))
    login = client.post(
        "/api/login", json={"email": email, "password": password})
    csrf = _cookie_value(login, "csrf_refresh_token")
    assert csrf
    refreshed = client.post("/api/refresh", headers={"X-CSRF-TOKEN": csrf})
    assert refreshed.status_code == 200
    new_access = refreshed.get_json()["access_token"]
    assert new_access

    # That fresh access token is accepted on a protected route.
    protected = client.get(
        "/api/protected", headers={"Authorization": f"Bearer {new_access}"}
    )
    assert protected.status_code == 200

    # Logout clears the refresh cookie, so a later refresh is rejected.
    logout = client.post("/api/logout")
    assert logout.status_code == 200
    after = client.post("/api/refresh", headers={"X-CSRF-TOKEN": csrf})
    assert after.status_code in (401, 422)


def test_login_missing_fields(client):
    response = client.post("/api/login", json={"email": "x@x.x"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing email and/or password"


def test_login_no_body(client):
    response = client.post("/api/login", json={})
    assert response.status_code == 400


def test_login_wrong_password(client, userInfo):
    email, password = userInfo
    client.post("/api/signup", json=_signup_payload(email, password))

    response = client.post(
        "/api/login", json={"email": email, "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid email or password"


def test_login_nonexistent_user(client, userInfo):
    email, password = userInfo
    response = client.post(
        "/api/login", json={"email": email, "password": password})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid email or password"


def _register_and_login(client, email, password="12345678"):
    client.post("/api/signup", json=_signup_payload(email, password))
    resp = client.post(
        "/api/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {resp.get_json()['access_token']}"}


def test_delete_account_requires_password(client, auth_headers):
    response = client.delete("/api/account", headers=auth_headers)
    assert response.status_code == 400


def test_delete_account_wrong_password(client, auth_headers, userInfo):
    email, _ = userInfo
    response = client.delete(
        "/api/account", json={"password": "not-the-password"}, headers=auth_headers
    )
    assert response.status_code == 400
    assert User.query.filter_by(email=email).first() is not None


def test_delete_account_cascades_everything(client, auth_headers, userInfo, post_id):
    _, a_password = userInfo
    a_id = User.query.filter_by(email=userInfo[0]).first().id
    post_a = post_id  # A's post

    # A second user who engages with A's content and has their own post.
    b_headers = _register_and_login(client, "other@test.test")
    b_id = User.query.filter_by(email="other@test.test").first().id

    # B engages with A's post.
    client.post("/api/like", json={"postId": post_a}, headers=b_headers)
    client.post(
        "/api/reply", json={"postId": post_a, "reply_text": "hi"}, headers=b_headers
    )

    # A engages with A's own post.
    client.post("/api/dislike", json={"postId": post_a}, headers=auth_headers)
    client.post(
        "/api/reply",
        json={"postId": post_a, "reply_text": "mine"},
        headers=auth_headers,
    )

    # B has a post; A engages with it (A's activity on someone else's content).
    client.post(
        "/api/post", json={"title": "B post", "description": "b"}, headers=b_headers
    )
    post_b = Post.query.filter_by(user_id=b_id).first().id
    client.post("/api/like", json={"postId": post_b}, headers=auth_headers)
    client.post(
        "/api/reply",
        json={"postId": post_b, "reply_text": "on b"},
        headers=auth_headers,
    )

    # A nested reply by B pointing at A's reply on B's post (built directly,
    # since the API only creates top-level replies).
    a_reply_on_b = Replies.query.filter_by(
        userReplied=a_id, postId=post_b).first()
    child = Replies(
        postId=post_b,
        userReplied=b_id,
        reply_text="child",
        parent_reply_id=a_reply_on_b.id,
    )
    db.session.add(child)
    db.session.commit()
    child_id = child.id

    resp = client.delete(
        "/api/account", json={"password": a_password}, headers=auth_headers
    )
    assert resp.status_code == 200
    db.session.expire_all()

    # A and everything A owns is gone (incl. other people's engagement on it).
    assert User.query.get(a_id) is None
    assert Post.query.get(post_a) is None
    assert Replies.query.filter_by(postId=post_a).count() == 0
    assert PostLikes.query.filter_by(postId=post_a).count() == 0
    assert PostDislikes.query.filter_by(postId=post_a).count() == 0

    # A's activity on other people's content is gone.
    assert Replies.query.filter_by(userReplied=a_id).count() == 0
    assert PostLikes.query.filter_by(userSentLike=a_id).count() == 0

    # B and B's post survive; B's child reply survives with its parent detached.
    assert User.query.get(b_id) is not None
    assert Post.query.get(post_b) is not None
    surviving_child = Replies.query.get(child_id)
    assert surviving_child is not None
    assert surviving_child.parent_reply_id is None
