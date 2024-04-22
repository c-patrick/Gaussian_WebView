import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    session,
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    login_required,
    current_user,
    logout_user,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Numeric, inspect
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal, DecimalException
from datatables import ColumnDT, DataTables
import json
from pathlib import Path

# File paths
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = "json"


app = Flask(__name__)
app.secret_key = "super secret key"
dir_path = os.path.dirname(os.path.realpath(__file__))
app.config["UPLOAD_FOLDER"] = dir_path + "/uploads"
print(f"Upload Folder: {app.config['UPLOAD_FOLDER']}")
app.static_folder = "static"

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
# Create the extension
db = SQLAlchemy(model_class=Base)
# initialise the app with the extension
db.init_app(app)


# Create User Table
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))


# Create Data Table
class QC_data(db.Model):
    __tablename__ = "data"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    qc_name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    HOMO: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    LUMO: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    Eg: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    Energy: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    Dipole: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    Quadrupole: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)


# Create table schema in the database. Requires application context.
with app.app_context():
    db.create_all()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Converts an SQLAlchemy object to dictionary
def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def make_decimal(dict):
    """Converts all numeric values in a dictionary to a Decimal type"""
    for key, value in dict.items():
        try:
            value = Decimal(value)
        except (ValueError, DecimalException):
            pass
    return dict


def process_json(file_path):
    filename = Path(file_path).stem
    with open(file_path) as file:
        data = json.load(file)
    data = data[filename]
    # Calculate Eg
    data["Eg"] = data["LUMO"] - data["HOMO"]
    # Calculate Qpi
    Q_pi = data["Quadrupole"]["ZZ"] * 0.743 * 3
    # Prepare data
    data_to_add = QC_data(
        qc_name=filename,
        HOMO=data["HOMO"],
        LUMO=data["LUMO"],
        Eg=data["Eg"],
        Energy=data["SCF Energy"],
        Dipole=data["Dipole"]["Tot"],
        Quadrupole=Q_pi,
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


@app.route("/")
def home():
    # READ ALL RECORDS
    # Construct a query to select from the database. Returns the rows in the database
    result = db.session.execute(db.select(QC_data).order_by(QC_data.qc_name))
    # Use .scalars() to get the elements rather than entire rows from the database
    all_data = result.scalars()
    return render_template(
        "index.html", data=all_data, logged_in=current_user.is_authenticated
    )


@app.route("/dt")
def dt():
    """List users with DataTables <= 1.10.x."""
    return render_template("dt.html", project="dt")


@app.route("/data")
def data():
    # Define columns
    columns = [
        ColumnDT(QC_data.qc_name),
        ColumnDT(QC_data.HOMO),
        ColumnDT(QC_data.LUMO),
        ColumnDT(QC_data.Eg),
        ColumnDT(QC_data.Energy),
        ColumnDT(QC_data.Dipole),
        ColumnDT(QC_data.Quadrupole),
    ]
    # Define query
    query = db.session.query().select_from(QC_data)
    # GET parameters
    params = request.args.to_dict()
    print(f"Parameters: {params}")
    # Instancing a DataTable for the query and table needed
    rowTable = DataTables(params, query, columns)
    # Return what is required by DataTable
    return jsonify(rowTable.output_result())


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        if user:
            # If user exists
            flash("You've already signed up with that email. Try logging in.")
            return redirect(url_for("login"))

        hashed_salted_password = generate_password_hash(
            request.form.get("password"), method="pbkdf2:sha256", salt_length=8
        )
        new_user = User(
            email=request.form.get("email"),
            password=hashed_salted_password,
            name=request.form.get("name"),
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))

    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        if not user:
            # User does not exist
            flash("That email does not exist, please try again.")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            flash("Incorrect password. Please try again.")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for("home"))
    if current_user.is_authenticated:
        flash("You are already logged in.")
        return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/upload", methods=["GET", "POST"])
@login_required
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
            error = process_json(file_path)
            if error:
                # If error encountered
                return redirect(url_for("compare"))
            else:
                return redirect(url_for("home"))
    return render_template("upload.html")


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        ## ToDo
        # Convert to dict and parse through a formatting function
        _qc_name = request.form["qc_name"]
        _HOMO = Decimal(request.form["HOMO"])
        _LUMO = Decimal(request.form["LUMO"])
        _Eg = round(_LUMO - _HOMO, 1)
        _Energy = Decimal(request.form["Energy"])
        # CREATE RECORD
        new_data = QC_data(
            qc_name=_qc_name, HOMO=_HOMO, LUMO=_LUMO, Eg=_Eg, Energy=_Energy
        )
        db.session.add(new_data)
        db.session.commit()
        return redirect(url_for("home"))
    if current_user.is_authenticated:
        return render_template("add.html")
    else:
        flash("Please authenticate to add data.")
        return redirect(url_for("login"))


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        # UPDATE RECORD
        new_data = {}
        data_id = request.form["id"]
        data_to_update = db.get_or_404(QC_data, data_id)
        form_data = request.form.to_dict()
        print(form_data)
        for key, value in form_data.items():
            if value != "":
                new_data[key] = value
        # Convert to correct data type for database
        make_decimal(new_data)
        # Write updated values to database
        for key, value in new_data.items():
            setattr(data_to_update, key, value)
        db.session.commit()
        db.session.flush()
        return redirect(url_for("home"))
    if current_user.is_authenticated:
        data_id = request.args.get("id")
        data_selected = db.get_or_404(QC_data, data_id)
        return render_template("edit.html", data=data_selected)
    else:
        flash("Please authenticate to edit data.")
        return redirect(url_for("login"))


@app.route("/compare", methods=["GET", "POST"])
@login_required
def compare():
    if request.method == "POST":
        return redirect(url_for("home"))
    data_to_add = session["new_data"]
    if data_to_add == {}:
        existing_data = {}
    else:
        existing_data = QC_data.query.filter_by(qc_name=data_to_add["qc_name"]).scalar()
    return render_template(
        "compare.html", existing_data=existing_data, data_to_add=data_to_add
    )


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


@app.route("/update_or_ignore", methods=["POST"])
def update_or_ignore():
    if "keep_data" in request.form:
        # Keep existing data, remove temp data
        # Clear session data
        session["new_data"] = {}
        return redirect(url_for("home"))
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
        return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
