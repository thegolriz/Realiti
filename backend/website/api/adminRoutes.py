import os
import urllib.parse
from datetime import datetime, timezone
from functools import wraps

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from website import db
from website.models import Post, RealtorAccount, Report, User

from .s3Routes import create_presigned_url

adminRoutes = Blueprint("adminRoutes", __name__)

# Known-safe content types, so the browser renders these inline instead of
# downloading them. Anything else just gets ResponseContentDisposition set,
# with no type override.
_DOCUMENT_CONTENT_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".pdf": "application/pdf",
}


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


def _iso(dt):
    return dt.isoformat() if dt else None


def _serialize_application(application):
    user = User.query.get(application.user_id)
    return {
        "id": application.id,
        "user_id": application.user_id,
        "account_name": f"{user.first_name} {user.last_name}" if user else None,
        "first_name": application.first_name,
        "last_name": application.last_name,
        "license_number": application.license_number,
        "state": application.state,
        "city": application.city,
        "email": application.email,
        "status": application.status,
        "submitted_at": _iso(application.submitted_at),
        "email_confirmed_at": _iso(application.email_confirmed_at),
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
    if post.s3_url:
        post.verification_status = "pending"
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


@adminRoutes.route("/admin/pending_verification", methods=["GET"])
@admin_required
def open_pending_verification():
    pending = Post.query.filter_by(verification_status="pending").all()
    return jsonify([_serialize_post(p) for p in pending]), 200


@adminRoutes.route("/admin/verify_posts/<int:post_id>/document-url", methods=["GET"])
@admin_required
def get_document_url(post_id):
    post = Post.query.get(post_id)
    if not post or not post.s3_url:
        return jsonify({"error": "No document for this post"}), 404
    key = urllib.parse.unquote(post.s3_url.split("/")[-1])
    _, ext = os.path.splitext(key.lower())
    extra_params = {"ResponseContentDisposition": "inline"}
    if ext in _DOCUMENT_CONTENT_TYPES:
        extra_params["ResponseContentType"] = _DOCUMENT_CONTENT_TYPES[ext]
    url = create_presigned_url(
        os.getenv("S3_BUCKET"),
        key,
        os.getenv("S3_REGION"),
        client_method="get_object",
        extra_params=extra_params,
    )
    if url is None:
        return jsonify({"error": "Failed to create document URL"}), 400
    return jsonify({"url": url}), 200


@adminRoutes.route("/admin/verify_posts/<int:post_id>/verify", methods=["POST"])
@admin_required
def verifiy_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post does not exist"}), 404
    post.verification_status = "verified"
    db.session.commit()
    return jsonify({"message": "Post verified"})


@adminRoutes.route("/admin/verify_posts/<int:post_id>/reject", methods=["POST"])
@admin_required
def reject_verification(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post does not exist"}), 404
    post.verification_status = None
    db.session.commit()
    return jsonify({"message": "Post does not meet verification standards"}), 200


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


@adminRoutes.route("/admin/realtor-applications", methods=["GET"])
@admin_required
def show_realtor_verification():
    apps = (
        RealtorAccount.query.filter_by(status="pending")
        .order_by(RealtorAccount.submitted_at)
        .all()
    )
    return jsonify([_serialize_application(a) for a in apps]), 200


@adminRoutes.route(
    "/admin/realtor-applications/<int:application_id>/approve", methods=["POST"]
)
@admin_required
def approve_realtor_application(application_id):
    application = RealtorAccount.query.get(application_id)
    if not application:
        return jsonify({"error": "Application does not exist"}), 404
    # Only confirmed applications; never one still waiting on its email or
    # already decided.
    if application.status != "pending":
        return jsonify({"error": "Only pending applications can be approved"}), 400
    # Apply only blocks on verified licenses, so two pending applications can
    # share one. Approving the second would give two accounts the badge.
    claimed = RealtorAccount.query.filter(
        RealtorAccount.id != application.id,
        RealtorAccount.license_number == application.license_number,
        RealtorAccount.state == application.state,
        RealtorAccount.status == "verified",
    ).first()
    if claimed:
        return (
            jsonify(
                {"error": "This license is already verified on another account"}),
            409,
        )
    application.status = "verified"
    application.verified_at = datetime.now(tz=timezone.utc)
    db.session.commit()
    return jsonify({"message": "Application approved"}), 200


@adminRoutes.route(
    "/admin/realtor-applications/<int:application_id>/reject", methods=["POST"]
)
@admin_required
def reject_realtor_application(application_id):
    data = request.get_json(silent=True) or {}
    application = RealtorAccount.query.get(application_id)
    if not application:
        return jsonify({"error": "Application does not exist"}), 404
    if application.status != "pending":
        return jsonify({"error": "Only pending applications can be rejected"}), 400
    application.status = "rejected"
    # Kept so "why was I rejected?" has an answer later.
    application.rejection_reason = data.get("reason")
    db.session.commit()
    return jsonify({"message": "Application rejected"}), 200
