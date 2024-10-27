from flask import render_template, request, jsonify
from datatables import ColumnDT, DataTables
from app.extensions import db
from app.models.qc_data import QC_data

from app.dt import bp


@bp.route("/")
def index():
    """List QC Data with DataTables"""
    return render_template("dt.html", project="dt")


@bp.route("/data")
def data():
    # Define columns
    columns = [
        ColumnDT(QC_data.id),
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
    # print(f"Parameters: {params}") # For debugging
    # Instancing a DataTable for the query and table needed
    rowTable = DataTables(params, query, columns)
    # Return what is required by DataTable
    return jsonify(rowTable.output_result())
