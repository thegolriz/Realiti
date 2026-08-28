from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    set_refresh_cookies,
    unset_jwt_cookies,
)

from website import db, limiter
from website.models import Post, PostDislikes, PostLikes, Replies, User
from website.security import DUMMY_HASH, hash_password, needs_rehash, verify_password

auth_routes = Blueprint("auth_routes", __name__)


@auth_routes.route("/login", methods=["POST"])
@limiter.limit(
    "10 per minute; 100 per day",
    deduct_when=lambda response: response.status_code == 401,
)
def login_api():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Missing email and/or password"}), 400
    email = data["email"]
    password = data["password"]

    user = User.query.filter_by(email=email).first()

    if user:
        password_matches = verify_password(user.password, password)
        if password_matches and needs_rehash(user.password):
            user.password = hash_password(password)
            db.session.commit()
    else:
        verify_password(DUMMY_HASH, password)
        password_matches = False

    if user and password_matches:
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        # Refresh token goes in an httpOnly cookie, not the body.
        resp = jsonify({"access_token": access_token})
        set_refresh_cookies(resp, refresh_token)
        return resp, 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401


@auth_routes.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404
    return jsonify({"message": f"Hello user {user.email}!"}), 200


@auth_routes.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    new_token = create_access_token(identity=user_id)
    return jsonify(access_token=new_token), 200


@auth_routes.route("/logout", methods=["DELETE", "POST"])
def logout_api():
    # Server has to clear the httpOnly refresh cookie; the client can't.
    resp = jsonify({"message": "logged out"})
    unset_jwt_cookies(resp)
    return resp, 200


@auth_routes.route("/signup", methods=["POST"])
@limiter.limit("5 per hour; 20 per day")
def signup_api():
    data = request.get_json()
    if (
        not data
        or "email" not in data
        or "first_name" not in data
        or "last_name" not in data
        or "password" not in data
    ):
        return jsonify({"error": "Missing required fields"}), 400

    email = data.get("email")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    password = data.get("password")

    if len(password) < 15:
        return jsonify({"error": "Password must be at least 15 characters long"}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return (
            jsonify(
                {"error": "An account with that email already exists. Try signing in."}
            ),
            400,
        )
    password = hash_password(password)
    new_user = User(
        email=email, password=password, first_name=first_name, last_name=last_name
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "account created"}), 201


@auth_routes.route("/account", methods=["GET"])
@jwt_required()
def get_account():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "user not found"}), 404
    return (
        jsonify(
            {
                "id": user.id,
                "first_name": user.first_name,
                "email": user.email,
                "is_admin": user.is_admin,
            }
        ),
        200,
    )


@auth_routes.route("/account/password", methods=["PATCH"])
@jwt_required()
def change_password():
    data = request.get_json(silent=True) or {}
    current_password = data.get("current_password")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")
    if not current_password or not new_password or not confirm_password:
        return jsonify({"error": "All password fields are required"}), 400

    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "user not found"}), 404

    if not verify_password(user.password, current_password):
        return jsonify({"error": "Current password is incorrect"}), 400
    if new_password != confirm_password:
        return jsonify({"error": "New passwords do not match"}), 400
    if len(new_password) < 15:
        return jsonify({"error": "Password must be at least 15 characters long"}), 400

    user.password = hash_password(new_password)
    db.session.commit()
    return jsonify({"message": "password updated"}), 200


@auth_routes.route("/account", methods=["DELETE"])
@jwt_required()
def delete_account():
    data = request.get_json(silent=True) or {}
    password = data.get("password")
    if not password:
        return jsonify({"error": "Password required to delete account"}), 400

    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "user not found"}), 404

    if not verify_password(user.password, password):
        return jsonify({"error": "Invalid password"}), 400

    uid = user.id
    try:
        # Deleting the user's posts also removes every reply/like/dislike on
        # them (including other people's), since those rows can't outlive the
        # post they hang off of.
        post_ids = [p.id for p in Post.query.filter_by(user_id=uid).all()]
        if post_ids:
            Replies.query.filter(Replies.postId.in_(post_ids)).delete(
                synchronize_session=False
            )
            PostLikes.query.filter(PostLikes.postId.in_(post_ids)).delete(
                synchronize_session=False
            )
            PostDislikes.query.filter(PostDislikes.postId.in_(post_ids)).delete(
                synchronize_session=False
            )

        # The user's own replies on other people's posts. Detach any child
        # replies that point at them (those belong to other users, on other
        # people's posts) so those threads survive with a null parent.
        my_reply_ids = [r.id for r in Replies.query.filter_by(
            userReplied=uid).all()]
        if my_reply_ids:
            Replies.query.filter(Replies.parent_reply_id.in_(my_reply_ids)).update(
                {Replies.parent_reply_id: None}, synchronize_session=False
            )
            Replies.query.filter_by(userReplied=uid).delete(
                synchronize_session=False)

        # The user's likes/dislikes on other people's posts.
        PostLikes.query.filter_by(userSentLike=uid).delete(
            synchronize_session=False)
        PostDislikes.query.filter_by(userSentDislike=uid).delete(
            synchronize_session=False
        )

        # Finally the user's posts, then the user record itself.
        Post.query.filter_by(user_id=uid).delete(synchronize_session=False)
        db.session.delete(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to delete account"}), 500

    # The account is gone; clear the refresh cookie so no new tokens can be
    # minted. The stateless access token stays valid until it expires (<=15m).
    resp = jsonify({"message": "account deleted"})
    unset_jwt_cookies(resp)
    return resp, 200
