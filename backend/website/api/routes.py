from flask import Blueprint, jsonify

from website.models import Note, User
from flask_jwt_extended import get_jwt_identity, jwt_required

routes = Blueprint("routes", __name__)


@routes.route("/hello", methods=["GET"])
def hello_world():
    return jsonify({"message": "Hello from the API"})


@routes.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    users_list = [{"id": user.id, "email": user.email} for user in users]
    return jsonify(users_list)
