from flask import render_template, request, flash, redirect, url_for
import numpy as np

from app.chart import bp
from app.extensions import db
from app.models.qc_data import QC_data


def prepare_data(data):
    xy_labels = []
    # print(data)
    for x in data.keys():
        xy_labels.append(x)
    # print(xy_labels)
    x_list = data[xy_labels[0]]
    y_list = data[xy_labels[1]]
    xy_data = []
    for i in range(len(x_list)):
        temp = {
            "x": x_list[i],
            "y": y_list[i],
        }
        xy_data.append(temp)
    # print(xy_data)
    return xy_labels, xy_data

# TODO fix UV-vis maths
def convolute(data, datatype="", npoints=1000, hwhm=0.1, broad="Gau", input_bins=False):
    # from https://github.com/jcerezochem/analyze_spectra/
    """
    Make a Gaussian convolution of the stick spectrum
    The spectrum must be in energy(eV) vs Intens (LS?)

    Arguments:
    data  dictionary of data {label, [data]}
    npoints    int           number of points
    hwhm       float         half width at half maximum

    Retunrs a list of dictionaries of x,y coordinates in format:
    {'x': data, 'y': data}
    """
    xy_labels = []
    for x in data.keys():
        xy_labels.append(x)
    if datatype == "UV":
        # UV data extracted in reverse order
        x = list(reversed(data[xy_labels[0]]))
        y = list(reversed(data[xy_labels[1]]))
        print(f"X Labels: {x}")
    else:
        x = data[xy_labels[0]]
        y = data[xy_labels[1]]
    print(x)
    print(y)

    # ------------------------------------------------------------------------
    # Convert discrete sticks into a continuous function with an histogram
    # ------------------------------------------------------------------------
    # (generally valid, but the exact x values might not be recovered)
    # Make the histogram for an additional 20% (if the baseline is not recovered, enlarge this)
    extra_factor = 0.2
    recovered_baseline = False
    sigma = hwhm / np.sqrt(2.0 * np.log(2.0))
    while not recovered_baseline:
        if input_bins:
            npoints = len(x)
            xhisto = x
            yhisto = y
            width = x[1] - x[0]
        else:
            extra_x = (x[-1] - x[0]) * extra_factor
            yhisto, bins = np.histogram(
                x, range=[x[0] - extra_x, x[-1] + extra_x], bins=npoints, weights=y
            )
            # Use bin centers as x points
            width = bins[1] - bins[0]
            xhisto = bins[0:-1] + width / 2
        # ----------------------------------------
        # Build Gaussian (centered around zero)
        # ----------------------------------------
        dxgau = width
        # The same range as xhisto should be used
        # this is bad. We can get the same using
        # a narrower range and playing with sigma.. (TODO)
        if npoints % 2 == 1:
            # Zero is included in range
            xgau_min = -dxgau * (npoints / 2)
            xgau_max = +dxgau * (npoints / 2)
        else:
            # Zero is not included
            xgau_min = -dxgau / 2.0 - dxgau * ((npoints / 2) - 1)
            xgau_max = +dxgau / 2.0 + dxgau * ((npoints / 2) - 1)
        xgau = np.linspace(xgau_min, xgau_max, npoints)
        if broad == "Gau":
            ygau = np.exp(-(xgau**2) / 2.0 / sigma**2) / sigma / np.sqrt(2.0 * np.pi)
        elif broad == "Lor":
            ygau = hwhm / (xgau**2 + hwhm**2) / np.pi

        # ------------
        # Convolute
        # ------------
        # with mode="same", we get the original xhisto range.
        # Since the first moment of the Gaussian is zero,
        # xconv is exactly xhisto (no shifts)
        yconv = np.convolve(yhisto, ygau, mode="same")
        xconv = xhisto

        # Check baseline recovery (only with automatic bins
        if yconv[0] < yconv.max() / 100.0 and yconv[-1] < yconv.max() / 100.0:
            recovered_baseline = True
        if input_bins:
            recovered_baseline = True

        extra_factor = extra_factor + 0.05

        # For UV convolution
        if datatype == "UV":
            # Convert back linshape to intensity
            yconv *= xconv
            # Convert E[eV] to Wavelength[nm]
            # xconv = xconv / 1.23981e-4  # eV->cm-1
            # xconv = 1e7 / xconv  # cm-1 -> nm

        xy_data = []
        for i in range(len(xconv)):
            temp = {
                "x": xconv[i],
                "y": yconv[i],
            }
            xy_data.append(temp)
    return xy_labels, xy_data


@bp.route("/", methods=["GET", "POST"])
def index():
    # Get data type
    if request.method == "POST":
        id_selected = request.form.keys()
        id = ','.join(map(str, id_selected)) 
        return redirect(url_for("chart.index", id=id))
    data_id = request.args["id"]
    print(f"Request ID: {data_id}") # for debugging
    # Split multiple IDs into list
    data_id = data_id.split(",")
    # Convert to int
    try:
        data_id = list(map(int, data_id))
    except ValueError:
        flash("ID Error. Please try again.")
        return redirect(url_for("main.index"))
    print(f"Data ID: {data_id}") # for debugging
    # data_id = 1 # for debugging
    data = []
    data_flags = {
        "IR": False,
        "ES": False
    }
    for i in data_id:
        IR_data = None
        ES_data = None
        data_selected = db.get_or_404(QC_data, i)
        qc_name = data_selected.qc_name
        IR_xy_labels, IR_data = convolute(data_selected.Vibrations, hwhm=7.5)
        ES_xy_labels, ES_data = convolute(data_selected.ES, datatype="UV", hwhm=7.5)
        data_to_add = {}
        data_to_add |= {'name': qc_name} # merge to dict
        # Logic to deal with cases where no IR or ES data is present
        if IR_data is not None:
            data_to_add |= {'IR': IR_data} # merge to dict
            data_flags["IR"] = True
        if ES_data is not None:
            data_to_add |= {'ES': ES_data} # merge to dict
            data_flags["ES"] = True
        # Append data
        data.append(data_to_add)
    print(data) # for debugging
    return render_template("chart.html", data=data, flags=data_flags)

# Old below:
# @bp.route("/", methods=["GET", "POST"])
# def index():
#     # Get data type
#     if request.method == "POST":
#         pass
#     # data_id = request.args["id"]
#     data_id = 1
#     labels = {}
#     data = {}
#     data_selected = db.get_or_404(QC_data, data_id)
#     IR_xy_labels, IR_xy_data = convolute(data_selected.Vibrations, hwhm=7.5)
#     ES_xy_labels, ES_xy_data = convolute(data_selected.ES, datatype="UV", hwhm=7.5)
#     # Prepare data dict
#     if IR_xy_data:
#         data["IR"] = IR_xy_data
#     if ES_xy_data:
#         data["Excited States"] = ES_xy_data
#     print(labels)
#     print(data)
#     return render_template("chart.html", data=data)
