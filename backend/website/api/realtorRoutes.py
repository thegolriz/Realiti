from flask import Blueprint, jsonify, request
from website import db
from website.models import RealtorAccount, User
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask import current_app
from itsdangerous import URLSafeTimedSerializer
import os
from website.emailSender import send_verification_email
CONFIRM_SALT = "realtor-email-confirm"

realtorRoutes = Blueprint("realtorRoutes", __name__)

REQUIRED = ("email", "first_name", "last_name",
            "license_number", "state", "city")


def _confirm_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=CONFIRM_SALT)


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
        return jsonify({"error": "License should be 30 characters or less, if your license is longer than 30 characters, please contact support@realiti.dev"}), 400

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
    token = _confirm_serializer().dumps(
        {"application_id": application.id, "email": email})
    link = f"{os.getenv('FRONTEND_URL')}/realtor-verify/confirm?token={token}"
    response = {"message": "Application submitted. Check your email to confirm."}
    if not send_verification_email(email, link):
        response["warning"] = (
            "Your application was saved, but we couldn't send the confirmation "
            "email. Try resending it, or contact support@realiti.dev."
        )
    return jsonify(response), 201
