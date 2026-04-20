from flask import Blueprint, jsonify

from website.models import User
from flask_jwt_extended import get_jwt_identity, jwt_required

routes = Blueprint("routes", __name__)


@routes.route("/hello", methods=["GET"])
def hello_world():
    return jsonify({"message": "Hello from the API"})
