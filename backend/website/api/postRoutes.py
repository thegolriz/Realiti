import urllib.parse

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from website import db
from website.models import Post, PostDislikes, PostLikes

from .moderationRoute import (
    REASON_GUIDELINES,
    REASON_INAPPROPRIATE,
    moderation_check,
    regex_check,
)

postRoutes = Blueprint("postRoutes", __name__)


@postRoutes.route("/post", methods=["POST"])
@jwt_required()
def post_api():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Empty post"}), 400
    if "description" not in data:
        return (
            jsonify({"error": ("Please provide a description for your post.")}),
            400,
        )
    title = data["title"]
    description = data["description"]
    document = data.get("document")
    user_id = get_jwt_identity()
    s3_obj = urllib.parse.unquote(
        document.split("/")[-1]) if document else None
    if not moderation_check(s3_obj):
        return jsonify({"error": "This post contains inappropriate content"}), 400
    reason = regex_check(title, description)
    if reason == REASON_INAPPROPRIATE:
        return jsonify({"error": "This post contains inappropriate content"}), 400
    if reason == REASON_GUIDELINES:
        return jsonify({"error": "Post does not meet our guidelines"}), 400
    new_post = Post(
        user_id=user_id, title=title, description=description, s3_url=document
    )
    db.session.add(new_post)
    db.session.commit()
    return jsonify({"message": "Post created"}), 200


@postRoutes.route("/post", methods=["GET"])
@jwt_required(optional=True)
def post_get_api():
    user_id = get_jwt_identity()
    postInfo = Post.query.all()
    postList = []
    for post in postInfo:
        liked = False
        disliked = False
        if user_id:
            liked = (
                PostLikes.query.filter_by(
                    postId=post.id, userSentLike=user_id
                ).first()
                is not None
            )
            disliked = (
                PostDislikes.query.filter_by(
                    postId=post.id, userSentDislike=user_id
                ).first()
                is not None
            )
        postList.append(
            {
                "id": post.id,
                "title": post.title,
                "description": post.description,
                "name": post.user.first_name,
                "likes": PostLikes.query.filter_by(postId=post.id).count(),
                "dislikes": PostDislikes.query.filter_by(postId=post.id).count(),
                "liked": liked,
                "disliked": disliked,
            }
        )
    return jsonify(postList)
