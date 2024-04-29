from flask import Blueprint

bp = Blueprint("secret", __name__)

from app.secret import routes
