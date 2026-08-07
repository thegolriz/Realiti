from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from website import db
from website.models import Post, Replies, User

repliesRoutes = Blueprint("repliesRoutes", __name__)


@repliesRoutes.route("/reply", methods=["POST"])
@jwt_required()
def reply_api():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Reply failed, no data sent"}), 400
    postId = data.get("postId")
    reply_text = data.get("reply_text")
    if not reply_text:
        return jsonify({"error": "Reply text is required"}), 400
    userReplied = get_jwt_identity()
    postExists = Post.query.filter_by(id=postId).first()
    if not postExists:
        return jsonify({"error": "Post does not exist"}), 404
    replied = Replies(postId=postId, userReplied=userReplied, reply_text=reply_text)
    db.session.add(replied)
    db.session.commit()
    return jsonify({"reply sent": True}), 200


@repliesRoutes.route("/replies/<int:post_id>", methods=["GET"])
def get_replies(post_id):
    replies = Replies.query.filter_by(postId=post_id).order_by(Replies.replied_at).all()
    result = []
    for reply in replies:
        user = User.query.get(reply.userReplied)
        result.append(
            {
                "id": reply.id,
                "reply_text": reply.reply_text,
                "userId": reply.userReplied,
                "userName": user.first_name if user else "Unknown",
                "replied_at": (
                    reply.replied_at.isoformat() if reply.replied_at else None
                ),
            }
        )
    return jsonify(result), 200
