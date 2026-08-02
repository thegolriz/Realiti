from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    set_refresh_cookies,
    unset_jwt_cookies,
)
from website import db
from website.models import User
from website.security import DUMMY_HASH, hash_password, needs_rehash, verify_password

auth_routes = Blueprint("auth_routes", __name__)


@auth_routes.route("/login", methods=["POST"])
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
        return jsonify({"error": "Invalid email or password"}), 400


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

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "email in use"}), 400
    password = hash_password(password)
    new_user = User(
        email=email, password=password, first_name=first_name, last_name=last_name
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "account created"}), 201
