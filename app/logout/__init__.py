from flask import Blueprint

bp = Blueprint("logout", __name__)

from app.logout import routes
