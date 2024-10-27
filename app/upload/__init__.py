from flask import Blueprint, flash, session
import json
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError


from app.extensions import db, object_as_dict
from app.models.qc_data import QC_data

ALLOWED_EXTENSIONS = "json"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def process_json(file_path):
    filename = Path(file_path).stem
    with open(file_path) as file:
        data = json.load(file)
    # Loop through all entries in JSON file
    for qc_name, qc_data in data.items():
        # Calculate Eg
        qc_data["Eg"] = qc_data["LUMO"] - qc_data["HOMO"]
        # Calculate Qpi
        Q_pi = qc_data["Quadrupole"]["ZZ"] * 0.743 * 3
        # Prepare data
        data_to_add = QC_data(
            qc_name=qc_name,
            HOMO=qc_data["HOMO"],
            LUMO=qc_data["LUMO"],
            Eg=qc_data["Eg"],
            Energy=qc_data["SCF Energy"],
            Dipole=qc_data["Dipole"]["Tot"],
            Quadrupole=Q_pi,
            Vibrations=qc_data["Vibrations"],
            ES=qc_data["Excited States"],
        )
        db.session.add(data_to_add)
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            error = str(e.__dict__["orig"])
            if "UNIQUE" in error:
                error = f'Name "{data_to_add.qc_name}" already exists:'
            print(f"ERROR: {error}")
            flash(error)
            new_data = object_as_dict(data_to_add)
            print(new_data)
            session["new_data"] = new_data
            return error
    return


bp = Blueprint("upload", __name__)

from app.upload import routes
