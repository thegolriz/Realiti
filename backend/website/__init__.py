import os
from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_cors import CORS


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
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 86400
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)  # noqa: F841
    CORS(app, origins=["http://localhost:3000",
         "https://yourfuturefrontend.com"])
    from website.api.auth_routes import auth_routes  # noqa: F401
    from website.api.routes import routes  # noqa: F401
    from website.api.postRoutes import postRoutes  # noqa: F401
    from website.api.s3Routes import s3Routes
    app.register_blueprint(routes, url_prefix="/api")
    app.register_blueprint(auth_routes, url_prefix="/api")
    app.register_blueprint(postRoutes, url_prefix="/api")
    app.register_blueprint(s3Routes, url_prefix="/api")
    from .models import User, Post  # noqa: F401

    return app
