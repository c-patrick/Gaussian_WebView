from flask import Blueprint

bp = Blueprint("chart", __name__)

from app.chart import routes
