from flask import Blueprint

bp = Blueprint("update_or_ignore", __name__)

from app.update_or_ignore import routes
