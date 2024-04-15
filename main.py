import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
import json
from pathlib import Path

"""
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
"""

# File paths
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = "json"


app = Flask(__name__)
app.secret_key = "super secret key"
dir_path = os.path.dirname(os.path.realpath(__file__))
app.config["UPLOAD_FOLDER"] = dir_path + "/uploads"
print(f"Upload Folder: {app.config['UPLOAD_FOLDER']}")


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
# Create the extension
db = SQLAlchemy(model_class=Base)
# initialise the app with the extension
db.init_app(app)


# CREATE TABLE
class QC_data(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    qc_name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    HOMO: Mapped[float] = mapped_column(Float, nullable=False)
    LUMO: Mapped[float] = mapped_column(Float, nullable=False)
    Eg: Mapped[float] = mapped_column(Float, nullable=False)
    Energy: Mapped[Float] = mapped_column(Float, nullable=False)


# Create table schema in the database. Requires application context.
with app.app_context():
    db.create_all()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def process_json(file_path):
    filename = Path(file_path).stem
    with open(file_path) as file:
        data = json.load(file)
    data = data[filename]
    # Calculate Eg
    data["Eg"] = data["LUMO"] - data["HOMO"]
    # Prepare data
    new_data = QC_data(
        qc_name=filename,
        HOMO=data["HOMO"],
        LUMO=data["LUMO"],
        Eg=data["Eg"],
        Energy=data["SCF Energy"],
    )
    db.session.add(new_data)
    db.session.commit()
    return


@app.route("/")
def home():
    # READ ALL RECORDS
    # Construct a query to select from the database. Returns the rows in the database
    result = db.session.execute(db.select(QC_data).order_by(QC_data.qc_name))
    # Use .scalars() to get the elements rather than entire rows from the database
    all_data = result.scalars()
    return render_template("index.html", data=all_data)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        # Check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == "":
            flash("No file selected")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            process_json(file_path)
            return redirect(url_for("home"))
    return render_template("upload.html")


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        _qc_name = request.form["qc_name"]
        _HOMO = float(request.form["HOMO"])
        _LUMO = float(request.form["LUMO"])
        _Eg = round(_LUMO - _HOMO, 1)
        _Energy = float(request.form["Energy"])
        # CREATE RECORD
        new_data = QC_data(
            qc_name=_qc_name, HOMO=_HOMO, LUMO=_LUMO, Eg=_Eg, Energy=_Energy
        )
        db.session.add(new_data)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add.html")


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        # UPDATE RECORD
        data_id = request.form["id"]
        data_to_update = db.get_or_404(QC_data, data_id)
        if request.form["qc_name"] != 0:
            print("Updating Name")
            data_to_update.qc_name = request.form["qc_name"]
        if request.form["HOMO"] != "":
            print("Updating HOMO")
            data_to_update.HOMO = request.form["HOMO"]
            data_to_update.Eg = round(
                data_to_update.LUMO - float(request.form["HOMO"]), 1
            )
        if request.form["LUMO"] != "":
            print("Updating LUMO")
            data_to_update.LUMO = request.form["LUMO"]
            data_to_update.Eg = round(
                float(request.form["LUMO"]) - data_to_update.HOMO, 1
            )
        if request.form["Energy"] != "":
            print("Updating Energy")
            data_to_update.Energy = request.form["Energy"]
        db.session.commit()
        return redirect(url_for("home"))
    data_id = request.args.get("id")
    data_selected = db.get_or_404(QC_data, data_id)
    return render_template("edit.html", data=data_selected)


@app.route("/delete")
def delete():
    data_id = request.args.get("id")
    # DELETE A RECORD BY ID
    data_to_delete = db.get_or_404(QC_data, data_id)
    # Alternative way to select the book to delete.
    # book_to_delete = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    db.session.delete(data_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
