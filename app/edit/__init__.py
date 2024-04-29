from flask import Blueprint

bp = Blueprint("edit", __name__)

from app.edit import routes
