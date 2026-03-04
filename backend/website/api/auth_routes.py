from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import check_password_hash, generate_password_hash

from website import db
from website.models import User

auth_routes = Blueprint("auth_routes", __name__)


# the login api is down below
@auth_routes.route("/login", methods=["POST"])
def login_api():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Missing email and/or password"}), 409
    email = data["email"]
    password = data["password"]

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        return (
            jsonify(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires in": 3600,
                }
            ),
            200,
        )
    else:
        return jsonify({"error": "Invalid email or password"}), 401


# the protected login using jwt is below
@auth_routes.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    print("Received Headers:")
    auth_header = request.headers.get("Authorization")
    print(f"Received Authorization Header: {auth_header}")
    user_id = get_jwt_identity()
    print(f"Extracted user ID from JWT: {user_id}")
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "user not found"}), 401
    return jsonify({"message": f"Hello user {user.email}!"}), 200


# token refresh is below
@auth_routes.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)  # requries existing token
def refresh():
    user_id = get_jwt_identity()
    new_token = create_access_token(identity=user_id)
    return jsonify(access_token=new_token), 200


# logout is below
@auth_routes.route("/logout", methods=["DELETE", "POST"])
def logout_api():
    return jsonify({"message": "Logout endpoint"}), 200


# signup is below
@auth_routes.route("/signup", methods=["POST"])
def signup_api():
    data = request.get_json()
    email = data.get("email")
    first_name = data.get("firstName")
    last_name = data.get("lastName")
    password = data.get("password")

    if not email or not first_name or not last_name or not password:
        return jsonify({"error": "Missing required data fields"}), 409

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 409

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "email in use"}), 409
    else:
        # red underline is lsp error, code works fine so far
        password = generate_password_hash(password, method="scrypt", salt_length=16)
        print(password)
        new_user = User(
            email=email, password=password, first_name=first_name, last_name=last_name
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "account created"}), 200
