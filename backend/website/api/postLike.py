from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from website import db
from website.models import PostLikes, Post


postLike = Blueprint("postLikes", __name__)


@postLike.route("/like", methods=["POST"])
@jwt_required()
def like_api():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Like failed, no data sent"}), 400
    postId = data["postId"]
    userSentLike = get_jwt_identity()
    postExists = Post.query.filter_by(id=postId).first()
    if not postExists:
        return jsonify({"error": "Post does not exist"}), 404
    userCheck = PostLikes.query.filter_by(
        userSentLike=userSentLike, postId=postId).first()
    if userCheck:
        db.session.delete(userCheck)
        db.session.commit()
        return jsonify({"liked": False}), 200
    liked = PostLikes(postId=postId, userSentLike=userSentLike)
    db.session.add(liked)
    db.session.commit()
    return jsonify({"liked": True}), 200
