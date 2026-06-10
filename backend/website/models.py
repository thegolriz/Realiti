from datetime import datetime, timezone

from . import db  # same as putting what folder we are currently in


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(tz=timezone.utc))
    is_admin = db.Column(db.Boolean, default=False)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship("User", backref="posts")
    title = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    description = db.Column(db.Text, nullable=False)
    s3_url = db.Column(db.String, nullable=True)
    posted_at = db.Column(db.DateTime, default=datetime.now(tz=timezone.utc))


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
    replied_at = db.Column(db.DateTime, default=datetime.now(tz=timezone.utc))
    parent_reply_id = db.Column(db.Integer, db.ForeignKey("replies.id"), nullable=True)
