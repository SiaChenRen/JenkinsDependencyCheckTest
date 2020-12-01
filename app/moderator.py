import functools
import sys
import re

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, escape
from werkzeug.security import check_password_hash, generate_password_hash

from app.auth import login_required
from app.db import get_db
from app.logging import log_user_action


bp = Blueprint("moderator", __name__, url_prefix="/moderator")

def mod_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user") is None:
            return redirect(url_for("auth.login"))
        else:
            db = get_db()
            if not db.user_id_exists(session["user"]) and not db.mod_access(session["user"]):
                return redirect(url_for("auth.login"))
            
        return view(**kwargs)
    return wrapped_view


@bp.route("/post", methods=("GET", "POST"))
@mod_login_required
def moderator_view_post():
    if request.method == "GET":
        # Get Database
        db = get_db()

        # Retrieve all user post
        post_data = db.moderator_view()

        return render_template("admin/moderator-dashboard.html", post_data = post_data, page="post")

    return render_template("admin/moderator-dashboard.html")


@bp.route("/removepost", methods=("GET", "POST"))
@mod_login_required
@log_user_action
def moderator_remove_post():
    if request.method == "GET":
        # Retrieve and sanitize form variable
        if "post" in request.args:
            post_id = request.args["post"].strip()
        else:
            return render_template("moderator/post.html")
        
        # Get Database
        db = get_db()

        # Delete the post in database
        delete_result = db.moderator_delete_post(post_id)

        if delete_result != True:
            flash("Error in removing post.", "errors")
            return redirect(url_for("moderator.moderator_view_post"))    
        flash("Post successfully deleted.", "info")
        return redirect(url_for("moderator.moderator_view_post"))    

    return render_template("admin/moderator-dashboard.html")    


@bp.route("/user", methods=("GET", "POST"))
@mod_login_required
def moderator_view_user():
    if request.method == "GET":
        # Get Database
        db = get_db()

        # Retrieve all user post
        user_data = db.moderator_view_user()
        
        return render_template("admin/moderator-dashboard.html", user_data = user_data[1], page="user")
    return render_template("admin/moderator-dashboard.html")


@bp.route("/requestban", methods=("GET", "POST"))
@mod_login_required
@log_user_action
def moderator_request_ban_user():
    if request.method == "GET":
        # Retrieve and sanitize form variable
        if "user" in request.args:
            account_id = request.args["user"].strip()
        else:
            return render_template("moderator/user.html")
        
        # Get Database
        db = get_db()

        # Delete the post in database
        request_result = db.moderator_request_ban(account_id)

        if request_result != True:
            flash("Error in requesting user ban.", "errors")
            return redirect(url_for("moderator.moderator_view_user"))    
        flash("Request user ban successfully.", "info")
        return redirect(url_for("moderator.moderator_view_user"))    

    return render_template("admin/moderator-dashboard.html")    


@bp.route("/undorequestban", methods=("GET", "POST"))
@mod_login_required
@log_user_action
def morderator_undo_ban_request():
    if request.method == "GET":
        # Retrieve and sanitize form variable
        if "user" in request.args:
            account_id = request.args["user"].strip()
        else:
            return render_template("moderator/user.html")
        
        # Get Database
        db = get_db()

        # Delete the post in database
        request_result = db.morderator_undo_ban_request(account_id)

        if request_result != True:
            flash("Error in undo user ban request.", "errors")
            return redirect(url_for("moderator.moderator_view_user"))    
        flash("Undo user ban request successfully.", "info")
        return redirect(url_for("moderator.moderator_view_user"))    

    return render_template("admin/moderator-dashboard.html")    
    

    
