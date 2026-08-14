from datetime import datetime, timezone

from . import db  # same as putting what folder we are currently in


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tz=timezone.utc))
    is_admin = db.Column(db.Boolean, default=False)


class Realtor(db.Model):
    # Public directory of realtors. Rows can be added by any user (to tag a
    # realtor who may not have an account) and start unverified; verification
    # is a manual admin step once documents are provided.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)  # stored normalized (Title Case)
    state = db.Column(db.Text, nullable=False)  # stored normalized (UPPER)
    is_verified = db.Column(db.Boolean, default=False)
    # The account that *is* this realtor, once claimed and verified.
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    # The account that submitted the entry (often not the realtor themselves).
    added_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tz=timezone.utc))
    __table_args__ = (
        db.UniqueConstraint("name", "state", name="uq_realtor_name_state"),
    )


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship("User", backref="posts")
    title = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    description = db.Column(db.Text, nullable=False)
    s3_url = db.Column(db.String, nullable=True)
    posted_at = db.Column(db.DateTime, default=lambda: datetime.now(tz=timezone.utc))
    realtor_id = db.Column(db.Integer, db.ForeignKey("realtor.id"), nullable=True)
    # none -> pending (has a doc, awaiting admin) -> verified. Revocable by an
    # upheld report.
    verification_status = db.Column(db.String, default="none")
    verified_at = db.Column(db.DateTime, nullable=True)
    # clean (public) | pending_review (Claude unsure, hidden, in admin queue) |
    # removed (taken down by an admin). The public feed shows only "clean".
    review_status = db.Column(db.String, default="clean", server_default="clean")
    review_reason = db.Column(db.Text, nullable=True)


class PostLikes(db.Model):
    postId = db.Column(
        db.Integer, db.ForeignKey("post.id"), nullable=False, primary_key=True
    )
    userSentLike = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, primary_key=True
    )


class PostDislikes(db.Model):
    postId = db.Column(
        db.Integer, db.ForeignKey("post.id"), nullable=False, primary_key=True
    )
    userSentDislike = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, primary_key=True
    )


class Replies(db.Model):
    postId = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    userReplied = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    reply_text = db.Column(db.Text, nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    replied_at = db.Column(db.DateTime, default=lambda: datetime.now(tz=timezone.utc))
    parent_reply_id = db.Column(db.Integer, db.ForeignKey("replies.id"), nullable=True)


class Report(db.Model):
    # A complaint against a post, filed with proof. An upheld report is what
    # revokes a post's verified status ("human and machine error" safety valve).
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    reporter_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    evidence_url = db.Column(db.String, nullable=True)  # S3 proof
    status = db.Column(db.String, default="open")  # open | upheld | dismissed
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tz=timezone.utc))
    resolved_at = db.Column(db.DateTime, nullable=True)
