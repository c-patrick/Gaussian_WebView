from flask import Blueprint

bp = Blueprint("compare", __name__)

from app.compare import routes
