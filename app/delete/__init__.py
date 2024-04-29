from flask import Blueprint

bp = Blueprint("delete", __name__)

from app.delete import routes
