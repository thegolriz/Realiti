import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.exceptions import BadRequest, UnsupportedMediaType


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


def create_app():
    load_dotenv()

    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))
    load_dotenv(os.path.join(basedir, "..", "..", ".env"))

    # app configs here
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "SQLALCHEMY_DATABASE_URI")
    # jwt configs bewloer
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    # Short-lived access token (header), long-lived refresh token (httpOnly
    # cookie scoped to /api/refresh).
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
    app.config["JWT_REFRESH_COOKIE_PATH"] = "/api/refresh"
    # Off in dev so the cookie works over http://localhost; set to true in prod.
    app.config["JWT_COOKIE_SECURE"] = (
        os.getenv("JWT_COOKIE_SECURE", "false").lower() == "true"
    )
    app.config["JWT_COOKIE_SAMESITE"] = "Lax"
    app.config["JWT_COOKIE_CSRF_PROTECT"] = True
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate = Migrate(app, db, compare_type=True)  # noqa: F841
    jwt = JWTManager(app)  # noqa: F841
    CORS(
        app,
        origins=["http://localhost:3000", "https://realiti.dev"],
        supports_credentials=True,
    )

    # A malformed or non-JSON body makes request.get_json() raise before a
    # handler runs. Convert those werkzeug errors into the app's JSON error
    # shape so every endpoint returns a consistent {"error": ...} instead of
    # Flask's default HTML page.
    @app.errorhandler(BadRequest)
    def _handle_bad_request(err):
        return jsonify({"error": "Invalid or malformed request body"}), 400

    @app.errorhandler(UnsupportedMediaType)
    def _handle_unsupported_media(err):
        return jsonify({"error": "Request body must be JSON"}), 415

    from website.api.adminRoutes import adminRoutes
    from website.api.auth_routes import auth_routes  # noqa: F401
    from website.api.postDislike import postDislike
    from website.api.postLike import postLike
    from website.api.postRoutes import postRoutes  # noqa: F401
    from website.api.repliesRoutes import repliesRoutes
    from website.api.reportRoutes import reportRoutes
    from website.api.routes import routes  # noqa: F401
    from website.api.s3Routes import s3Routes

    app.register_blueprint(routes, url_prefix="/api")
    app.register_blueprint(auth_routes, url_prefix="/api")
    app.register_blueprint(postRoutes, url_prefix="/api")
    app.register_blueprint(s3Routes, url_prefix="/api")
    app.register_blueprint(postLike, url_prefix="/api")
    app.register_blueprint(postDislike, url_prefix="/api")
    app.register_blueprint(repliesRoutes, url_prefix="/api")
    app.register_blueprint(adminRoutes, url_prefix="/api")
    app.register_blueprint(reportRoutes, url_prefix="/api")
    from .models import (  # noqa: F401
        Post,
        PostDislikes,
        PostLikes,
        Realtor,
        Replies,
        Report,
        User,
    )

    return app
