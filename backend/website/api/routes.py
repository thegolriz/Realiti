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


@routes.route("/notes", methods=["GET"])
@jwt_required()
def get_user_notes():
    user_id = get_jwt_identity()
    notes = Note.query.filter_by(user_id=user_id).all()
    notes_list = [
        {"id": note.id, "data": note.data, "date": note.date.isoformat()}
        for note in notes
    ]
    return jsonify(notes_list)
