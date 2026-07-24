import urllib.parse

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from website import db
from website.models import Post, PostDislikes, PostLikes

from .claudeModeration import DECISION_BLOCK, DECISION_REVIEW, run_claude_checks
from .moderationRoute import (
    REASON_LEETSPEAK,
    REASON_PROFANITY,
    REASON_PROMPT_INJECTION,
    REASON_SPACING,
    moderation_check,
    regex_check,
)

postRoutes = Blueprint("postRoutes", __name__)

# Field-specific, guideline-referencing copy for each moderation reason.
# Keeping "title" and "description" wording distinct lets the user see
# exactly which field needs fixing when more than one is flagged.
MODERATION_MESSAGES = {
    REASON_PROFANITY: {
        "title": (
            "Your title contains profanity, which isn't permitted. Please "
            "revise your wording to meet our community guidelines."
        ),
        "description": (
            "Your post contains profanity, which isn't permitted. Please "
            "revise your wording to meet our community guidelines."
        ),
    },
    REASON_LEETSPEAK: {
        "title": (
            "Your title uses character substitutions that can be used to "
            "disguise flagged language. Please use standard spelling and "
            "review our community guidelines."
        ),
        "description": (
            "Your post uses character substitutions that can be used to "
            "disguise flagged language. Please use standard spelling and "
            "review our community guidelines."
        ),
    },
    REASON_SPACING: {
        "title": (
            "Your title has unusual spacing, which can be used to hide "
            "flagged content. Please remove the extra spacing and review "
            "our community guidelines."
        ),
        "description": (
            "Your post has unusual spacing, which can be used to hide "
            "flagged content. Please remove the extra spacing and review "
            "our community guidelines."
        ),
    },
    REASON_PROMPT_INJECTION: {
        "title": (
            "This submission does not meet our community guidelines. "
            "Please review and revise before resubmitting."
        ),
        "description": (
            "This submission does not meet our community guidelines. "
            "Please review and revise before resubmitting."
        ),
    },
}


def _moderation_error_messages(title_reason, description_reason):
    messages = []
    if title_reason:
        messages.append(MODERATION_MESSAGES[title_reason]["title"])
    if description_reason:
        messages.append(MODERATION_MESSAGES[description_reason]["description"])
    # Dedupe in case both fields hit the same (field-agnostic) reason.
    return list(dict.fromkeys(messages))


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
    # 1. Cheap regex screen on the text.
    title_reason, description_reason = regex_check(title, description)
    if title_reason or description_reason:
        errors = _moderation_error_messages(title_reason, description_reason)
        # "error" stays a single string for any caller that only reads that
        # field; "errors" carries each violation separately so the client
        # can surface them as distinct, trackable notifications.
        return jsonify({"error": errors[0], "errors": errors}), 400
    # 2. Rekognition screen on the media.
    if not moderation_check(s3_obj):
        return jsonify({"error": "This post contains inappropriate content"}), 400
    # 3. Claude layer: text, then media, then media-vs-description.
    verdict = run_claude_checks(title, description, s3_obj)
    if verdict and verdict.decision == DECISION_BLOCK:
        # TODO: map verdict.reason to guideline copy the way the regex
        # reasons are mapped above, rather than returning the raw reason.
        return jsonify({"error": verdict.reason}), 400
    if verdict and verdict.decision == DECISION_REVIEW:
        # Claude was unsure: persist the post but keep it out of the public
        # feed (review_status="pending_review") so an admin can approve or
        # remove it. verdict.reason is the context shown to the reviewer.
        held_post = Post(
            user_id=user_id,
            title=title,
            description=description,
            s3_url=document,
            review_status="pending_review",
            review_reason=verdict.reason,
        )
        db.session.add(held_post)
        db.session.commit()
        return (
            jsonify(
                {
                    "message": (
                        "Your post is being reviewed and will be published "
                        "once approved."
                    ),
                    "status": "pending_review",
                }
            ),
            202,
        )
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
    # Only "clean" posts are public; pending_review and removed stay hidden.
    postInfo = Post.query.filter_by(review_status="clean").all()
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
