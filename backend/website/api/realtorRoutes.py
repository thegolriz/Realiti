from flask import Blueprint, jsonify, request
from website import db
from website.models import RealtorAccount, User

realtorRoutes = Blueprint("realtorRoutes", __name__)
