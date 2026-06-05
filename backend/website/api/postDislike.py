from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from website import db
from website.models import PostDislikes, Post


postDislike = Blueprint("postDislikes", __name__)


@postDislike.route("/dislike", methods=["POST"])
@jwt_required()
def dislike_api():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dislike failed, no data sent"}), 400
    postId = data["postId"]
    userSentDislike = get_jwt_identity()
    postExists = Post.query.filter_by(id=postId).first()
    if not postExists:
        return jsonify({"error": "Post does not exist"}), 404
    userCheck = PostDislikes.query.filter_by(
        userSentDislike=userSentDislike, postId=postId).first()
    if userCheck:
        db.session.delete(userCheck)
        db.session.commit()
        return jsonify({"disliked": False}), 200
    disliked = PostDislikes(postId=postId, userSentDislike=userSentDislike)
    db.session.add(disliked)
    db.session.commit()
    return jsonify({"disliked": True}), 200
