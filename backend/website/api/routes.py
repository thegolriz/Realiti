from flask import Blueprint, jsonify

routes = Blueprint("routes", __name__)


@routes.route("/hello", methods=["GET"])
def hello_world():
    return jsonify({"message": "Hello from the API"})
