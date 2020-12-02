from flask import Blueprint, flash, g, redirect, render_template, request, url_for, escape
from werkzeug.exceptions import abort
import math


bp = Blueprint("common", __name__)


@bp.route("/", methods=("GET", "POST"))
def index():
    if request.method == "GET":
        return render_template("home.html")
    if request.method == "POST":
        try:
            password = request.form["password"]
            if (validatePassword(password)):
                return redirect(url_for("common.home"))
            else:
                return redirect(url_for("common.index"))
        except:
            return redirect(url_for("common.index"))

@bp.route("/home", methods=("GET", "POST"))
def home():
    if request.method == "GET":
        return render_template("welcome.html")

def validatePassword(password):
    if len(password) >= 8:
        return True
    return False