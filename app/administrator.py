import functools
import sys
import re

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, escape
from werkzeug.security import check_password_hash, generate_password_hash

from app.auth import login_required
from app.db import get_db
from app.logging import log_user_action


bp = Blueprint("administrator", __name__, url_prefix="/administrator")

def admin_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user") is None:
            return redirect(url_for("auth.login"))
        else:
            db = get_db()
            if not db.user_id_exists(session["user"]) and not db.admin_access(session["user"]):
                return redirect(url_for("auth.login"))
            
        return view(**kwargs)
    return wrapped_view


@bp.route("/user", methods=("GET", "POST"))
@admin_login_required
def administrator_view_user():
    if request.method == "GET":
        # Get Database
        db = get_db()

        # Retrieve all user post
        user_data = db.administrator_view_user()

        if user_data[0] == True :
            return render_template("admin/administrator-dashboard.html", user_data = user_data[1])
        

    return render_template("admin/administrator-dashboard.html")


@bp.route("/makemoderator", methods=("GET", "POST"))
@admin_login_required
@log_user_action
def make_moderator():
    if request.method == "GET":

        # Retrieve and sanitize form variable
        if "user" in request.args:
            account_id = request.args["user"].strip()
        else:
            return render_template("administrator/user.html")
    
        # Get Database
        db = get_db()

        # Update user to moderator role
        make_moderator_status = db.make_moderator(account_id)

        if make_moderator_status == False:
            flash("Error in making user to moderator.", "error")
            return redirect(url_for("administrator.administrator_view_user"))
        flash("User has been converted to moderator.", "info")
        return redirect(url_for("administrator.administrator_view_user"))

    return render_template("administrator/user.html")

@bp.route("/removemoderator", methods=("GET", "POST"))
@admin_login_required
@log_user_action
def remove_moderator():
    if request.method == "GET":

        # Retrieve and sanitize form variable
        if "user" in request.args:
            account_id = request.args["user"].strip()
        else:
            return render_template("administrator/user.html")
    
        # Get Database
        db = get_db()

        # Update user to user role
        make_moderator_status = db.remove_moderator(account_id)

        if make_moderator_status == False:
            flash("Error in making user to moderator.", "error")
            return redirect(url_for("administrator.administrator_view_user"))
        flash("User has been downgrade to user.", "info")
        return redirect(url_for("administrator.administrator_view_user"))

    return render_template("administrator/user.html")

@admin_login_required
def administrator_ban_user():
    pass

@admin_login_required
def administrator_send_password_reset():
    pass