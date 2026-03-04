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
migrate = Migrate()


def create_app():
    load_dotenv()

    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))
    load_dotenv(os.path.join(basedir, "..", "..", ".env"))

    # app configs here
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    # jwt configs bewloer
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 86400
    db.init_app(app)
    jwt = JWTManager(app)  # noqa: F841
    CORS(app, origins=["http://localhost:3000", "https://yourfuturefrontend.com"])
    from website.api.auth_routes import auth_routes  # noqa: F401
    from website.api.routes import routes  # noqa: F401

    app.register_blueprint(routes, url_prefix="/api")
    app.register_blueprint(auth_routes, url_prefix="/api")
    from .models import Note, User  # noqa: F401

    return app
