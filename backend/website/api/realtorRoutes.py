import os
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from website import db, limiter
from website.emailSender import send_verification_email
from website.models import RealtorAccount, User

CONFIRM_SALT = "realtor-email-confirm"

realtorRoutes = Blueprint("realtorRoutes", __name__)

REQUIRED = ("email", "first_name", "last_name", "license_number", "state", "city")


def _confirm_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=CONFIRM_SALT)


def _send_confirmation(application):
    # Shared by apply and resend. Each call signs a fresh token, so a resend
    # also restarts the 24 hour window.
    token = _confirm_serializer().dumps(
        {"application_id": application.id, "email": application.email}
    )
    link = f"{os.getenv('FRONTEND_URL')}/realtor-verify/confirm?token={token}"
    return send_verification_email(application.email, link)


@realtorRoutes.route("/send_verification", methods=["POST"])
@jwt_required()
def get_realtor_info():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing required fields"}), 400

    fields = {}
    for key in REQUIRED:
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            return jsonify({"error": "Missing required fields"}), 400
        fields[key] = value.strip()

    user = User.query.get(get_jwt_identity())
    if user is None:
        return (
            jsonify({"error": "The account requesting verification does not exist"}),
            404,
        )
    email = fields["email"].lower()
    # Signup stores emails as typed, so lowercase the stored one too.
    if email != user.email.strip().lower():
        return (
            jsonify(
                {
                    "error": "The email on file and requested email for verification "
                    "must match. If you need help please contact support@realiti.dev"
                }
            ),
            403,
        )

    license_number = fields["license_number"].upper()
    if len(license_number) > 30:
        return (
            jsonify(
                {
                    "error": "License numbers can be at most 30 characters. If "
                    "yours is longer, please contact support@realiti.dev"
                }
            ),
            400,
        )

    state = fields["state"].upper()
    city = fields["city"]

    # One active application per user; a rejected one can reapply.
    existing = RealtorAccount.query.filter(
        RealtorAccount.user_id == user.id,
        RealtorAccount.status.in_(["email_pending", "pending", "verified"]),
    ).first()
    if existing:
        messages = {
            "email_pending": "You already applied. Check your email to confirm it.",
            "pending": "Your application is already under review.",
            "verified": "Your account is already verified.",
        }
        return jsonify({"error": messages[existing.status]}), 409

    # Only a verified license blocks, so an impostor's pending application
    # can't lock the real agent out.
    claimed = RealtorAccount.query.filter(
        RealtorAccount.license_number == license_number,
        RealtorAccount.state == state,
        RealtorAccount.status == "verified",
    ).first()
    if claimed:
        return (
            jsonify(
                {
                    "error": "This license is already verified on another account. "
                    "If you need help please contact support@realiti.dev"
                }
            ),
            409,
        )

    application = RealtorAccount(
        user_id=user.id,
        first_name=fields["first_name"],
        last_name=fields["last_name"],
        license_number=license_number,
        state=state,
        city=city,
        email=email,
    )
    db.session.add(application)
    db.session.commit()
    response = {"message": "Application submitted. Check your email to confirm."}
    if not _send_confirmation(application):
        response["warning"] = (
            "Your application was saved, but we couldn't send the confirmation "
            "email. Try resending it, or contact support@realiti.dev."
        )
    return jsonify(response), 201


@realtorRoutes.route("/realtor/resend", methods=["POST"])
@jwt_required()
@limiter.limit("5 per hour")
def resend_confirmation():
    # Covers an expired link or a failed send. Without it, an email_pending
    # application blocks reapplying (409) with no way to finish.
    application = RealtorAccount.query.filter_by(
        user_id=int(get_jwt_identity()), status="email_pending"
    ).first()
    if application is None:
        return (
            jsonify({"error": "You don't have an application waiting on email"}),
            404,
        )
    if not _send_confirmation(application):
        return (
            jsonify(
                {
                    "error": "We couldn't send the confirmation email. Please try "
                    "again later, or contact support@realiti.dev."
                }
            ),
            502,
        )
    return jsonify({"message": "We sent a new confirmation link to your email."}), 200


@realtorRoutes.route("/realtor/confirm", methods=["POST"])
def confirm_realtor():
    # No login required: the signed token is the proof of inbox access, and the
    # link may be opened on a device that isn't signed in.
    data = request.get_json(silent=True)
    if not data or not data.get("token"):
        return jsonify({"error": "Missing token"}), 400
    try:
        payload = _confirm_serializer().loads(data["token"], max_age=86400)
    # SignatureExpired subclasses BadSignature, so it has to be caught first.
    except SignatureExpired:
        return (
            jsonify({"error": "This link has expired. Please request a new one."}),
            400,
        )
    except BadSignature:
        return jsonify({"error": "This link is invalid."}), 400

    application = RealtorAccount.query.get(payload["application_id"])
    if application is None:
        return jsonify({"error": "This application no longer exists."}), 404
    if application.email != payload["email"]:
        return (
            jsonify({"error": "This link no longer matches your application."}),
            400,
        )

    if application.status == "rejected":
        return (
            jsonify(
                {
                    "error": "This application was rejected. Please submit a new "
                    "one, or contact support@realiti.dev."
                }
            ),
            400,
        )
    # Already confirmed: a second click
    # isn't an error, so answer success without changing anything.
    if application.status == "pending":
        return (
            jsonify({"message": "Your email is already confirmed and under review."}),
            200,
        )
    if application.status == "verified":
        return jsonify({"message": "Your account is already verified."}), 200

    application.status = "pending"
    application.email_confirmed_at = datetime.now(tz=timezone.utc)
    db.session.commit()
    return (
        jsonify({"message": "Email confirmed. Your application is now under review."}),
        200,
    )
