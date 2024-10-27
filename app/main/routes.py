from flask import render_template
from flask_login import current_user
from app.main import bp
from app.extensions import db
from app.models.qc_data import QC_data


@bp.route("/")
def index():
    # READ ALL RECORDS
    # Construct a query to select from the database. Returns the rows in the database
    result = db.session.execute(db.select(QC_data).order_by(QC_data.id))
    # Use .scalars() to get the elements rather than entire rows from the database
    all_data = result.scalars()
    return render_template(
        "index.html", data=all_data, logged_in=current_user.is_authenticated
    )
