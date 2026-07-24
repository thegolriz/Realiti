from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from website import db
from website.models import Post, Report

reportRoutes = Blueprint("reportRoutes", __name__)


@reportRoutes.route("/report", methods=["POST"])
@jwt_required()
def create_report():
    data = request.get_json(silent=True) or {}
    post_id = data.get("postId")
    reason = data.get("reason")
    evidence_url = data.get("evidence_url")
    if not post_id or not reason:
        return jsonify({"error": "A post and a reason are required"}), 400
    if not Post.query.get(post_id):
        return jsonify({"error": "Post does not exist"}), 404
    report = Report(
        post_id=post_id,
        reporter_id=get_jwt_identity(),
        reason=reason,
        evidence_url=evidence_url,
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({"message": "Report submitted"}), 201
