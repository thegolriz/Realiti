from website import db
from website.models import User, Post
from flask_jwt_extended import (get_jwt_identity, jwt_required)
from flask import Blueprint, jsonify, request

postRoutes = Blueprint("postRoutes", __name__)


@postRoutes.route("/post", methods=["POST"])
@jwt_required()
def post_api():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Empty post"}), 400
    if "description" not in data:
        return jsonify({"error": "Please provide a description for your post."}), 400
    if "document" not in data:
        return jsonify({"error": "Please provide supporting evidance in the form of an image or pdf file."}), 400
    description = data["description"]
    document = data["document"]
    user_id = get_jwt_identity()
    new_post = Post(
        user_id=user_id, description=description, s3_url=document
    )
    db.session.add(new_post)
    db.session.commit()
    return jsonify({"message": "Post created"}), 200
