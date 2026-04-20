from website import db
import urllib.parse
from website.models import Post
from flask_jwt_extended import (get_jwt_identity, jwt_required)
from flask import Blueprint, jsonify, request
from .moderationRoute import moderation_check
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
    s3_obj = urllib.parse.unquote(document.split('/')[-1])
    passed = moderation_check(s3_obj)
    if (passed):
        new_post = Post(
            user_id=user_id, description=description, s3_url=document
        )
        db.session.add(new_post)
        db.session.commit()
        return jsonify({"message": "Post created"}), 200
    return jsonify({"error": "This post contains inappropriate content"}), 400


@postRoutes.route("/post", methods=["GET"])
def post_get_api():
    postInfo = Post.query.all()
    postList = []
    for post in postInfo:
        postList.append({
            "id": post.id,
            "title": post.title,
            "description": post.description,
            "name": post.user.first_name
        })
    return jsonify(postList)
