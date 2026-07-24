from datetime import datetime, timezone
from functools import wraps

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from website import db
from website.models import Post, Report, User

adminRoutes = Blueprint("adminRoutes", __name__)


def admin_required(fn):
    """jwt_required plus an is_admin check; 403 for non-admins."""

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = User.query.get(get_jwt_identity())
        if not user or not user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)

    return wrapper


def _serialize_post(post):
    return {
        "id": post.id,
        "title": post.title,
        "description": post.description,
        "name": post.user.first_name if post.user else "Unknown",
        "s3_url": post.s3_url,
        "review_status": post.review_status,
        "review_reason": post.review_reason,
    }


@adminRoutes.route("/admin/review-posts", methods=["GET"])
@admin_required
def review_posts():
    posts = Post.query.filter_by(review_status="pending_review").all()
    return jsonify([_serialize_post(p) for p in posts]), 200


@adminRoutes.route("/admin/review-posts/<int:post_id>/approve", methods=["POST"])
@admin_required
def approve_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post does not exist"}), 404
    post.review_status = "clean"
    db.session.commit()
    return jsonify({"message": "Post approved"}), 200


@adminRoutes.route("/admin/review-posts/<int:post_id>/reject", methods=["POST"])
@admin_required
def reject_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post does not exist"}), 404
    post.review_status = "removed"
    db.session.commit()
    return jsonify({"message": "Post removed"}), 200


@adminRoutes.route("/admin/reports", methods=["GET"])
@admin_required
def open_reports():
    reports = Report.query.filter_by(status="open").all()
    result = []
    for report in reports:
        post = Post.query.get(report.post_id)
        result.append(
            {
                "id": report.id,
                "reason": report.reason,
                "evidence_url": report.evidence_url,
                "post": _serialize_post(post) if post else None,
            }
        )
    return jsonify(result), 200


@adminRoutes.route("/admin/reports/<int:report_id>/resolve", methods=["POST"])
@admin_required
def resolve_report(report_id):
    data = request.get_json(silent=True) or {}
    action = data.get("action")  # "dismiss" or "uphold"
    report = Report.query.get(report_id)
    if not report:
        return jsonify({"error": "Report does not exist"}), 404
    if action not in ("dismiss", "uphold"):
        return jsonify({"error": "action must be 'dismiss' or 'uphold'"}), 400
    report.status = "dismissed" if action == "dismiss" else "upheld"
    report.resolved_at = datetime.now(tz=timezone.utc)
    # Upholding a report takes the post down (hidden from the public feed).
    if action == "uphold":
        post = Post.query.get(report.post_id)
        if post:
            post.review_status = "removed"
    db.session.commit()
    return jsonify({"message": f"Report {report.status}"}), 200
