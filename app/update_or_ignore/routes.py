from flask import redirect, url_for, request, session
from app.extensions import make_decimal

from app.update_or_ignore import bp
from app.extensions import db
from app.models.qc_data import QC_data


@bp.route("/", methods=["POST"])
def index():
    if "keep_data" in request.form:
        # Keep existing data, remove temp data
        # Clear session data
        session["new_data"] = {}
        return redirect(url_for("main.index"))
    if "replace_data" in request.form:
        # Replace existing data with new data
        new_data = session["new_data"]
        del new_data["id"]
        # Calculate Eg
        new_data["Eg"] = new_data["LUMO"] - new_data["HOMO"]
        # Get existing data
        existing_data = QC_data.query.filter_by(qc_name=new_data["qc_name"]).first()
        # Convert to correct data types for the database
        data_to_add = make_decimal(new_data)
        # Update each column for the existing data
        for key, value in data_to_add.items():
            setattr(existing_data, key, value)
        db.session.commit()
        db.session.flush()
        return redirect(url_for("main.index"))
