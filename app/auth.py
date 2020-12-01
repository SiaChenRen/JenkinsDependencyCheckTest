import functools
import sys
import re

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, escape
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf.csrf import CSRFProtect

from app.db import get_db
from app.logging import log_user_action


bp = Blueprint("auth", __name__, url_prefix="/auth")


# Decorator to redirects anonymous or invalid users to the login page.
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user") is None:
            return redirect(url_for("auth.login"))
        else:
            db = get_db()
            if not db.user_id_exists(session["user"]):
                return redirect(url_for("auth.login"))
            
        return view(**kwargs)
    return wrapped_view


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.
    Validates that the username is not already taken. Hashes the password for security.
    """
    if request.method == "POST":
        # Retrieve and sanitize form variable
        try:
            email = str(escape(request.form["email"].strip()))
            password = str(escape(request.form["password"].strip()))
            confirmPassword = str(escape(request.form["confirmpassword"].strip()))
        except:
            error = "Error in registering account."
            return render_template("auth/register.html", error=error)
            
        # Validate email if meet the requirement of Not Empty, have a "@" and "."
        email_result = validate_email(email)
        if email_result[0] != True:
            error = email_result[1]
            return render_template("auth/register.html", error=error)

        # Validate password and confirm password if it meet the requirement of Not Empty, 
        # have maximum length of 64 and minimum length of 8, password match with confirm password
        password_result = validate_passwords(password, confirmPassword)
        if password_result[0] != True:
            error = password_result[1]
            return render_template("auth/register.html", error=error)

        # Get Database
        db = get_db()

        # Check if there is existing account with same email
        if db.user_exists(email):
            error = 'Invalid Email/Password.'
            return render_template("auth/register.html", error=error)

        # Register account
        if db.register(email, password) == False:
            error = "Invalid Email/Password."
            return render_template("auth/register.html", error=error)
        else:
            info = "Account has been successfully created"
            return render_template("auth/register.html" , info=info)
        
        # Unexpected errors
        error = "Error in registering account."
        return render_template("auth/register.html", error=error)

    # Render register template if the method is not POST
    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        # Retrieve and sanitize form variable
        try:
            email = str(escape(request.form["email"].strip()))
            password = str(escape(request.form["password"].strip()))
        except:
            error = "Error in login in account"
            return render_template("auth/register.html", error=error)

        # Validate email if meet the requirement of Not Empty, have a "@" and "."
        email_result = validate_email(email)
        if email_result[0] != True:
            error = email_result[1]
            return render_template("auth/login.html", error=error)
        
        # Validate password if it meet the requirement of Not Empty, 
        # have maximum length of 64 and minimum length of 8
        password_result = validate_password(password)
        if password_result[0] != True:
            error = password_result[1]
            return render_template("auth/login.html", error=error)

        # Get Database
        db = get_db()

        # Attempt to authenticate the user
        result = db.login(email, password)
        if result[0] == False:
            error = result[1]
            return render_template("auth/login.html", error=error)

        # Successful login
        if result[0] == True:
            return redirect(url_for("index"))

    # Render login template if the method is not POST
    return render_template("auth/login.html")


@bp.route("/logout")
@log_user_action
def logout():
    # Clear all session, including the stored user id. Redirect to main page
    session.clear()
    return redirect(url_for("index"))


# Verify accounts using GET parameters
@bp.route("/verify", methods=["GET"])
def verify():
    user_id = request.args.get("id")
    token = request.args.get("token")

    db = get_db()
    if db.verify_account(user_id, token):
        message = "Successfully verified account"
        
    return redirect(url_for("auth.login"))



# Helper functions

# Validate email
def validate_email(email):
    # Check if the email is empty 
    if email == '':
        error = 'Please provide a email address.'
        return [False, error]

    # Check if the email is valid
    regex = "^[A-Za-z0-9]+[\._]?[A-Za-z0-9_]+[@]\w+[.]\w{2,3}$"
    if not re.match(regex, email):
        error = 'Please enter a valid email address.'
        return [False, error]
    
    return [True, "Email is validated"]

# Validate password
def validate_password(password):
    # Check if the password is empty
    if password == '':
        error = 'Please provide a password.'
        return [False, error]

    # Set password above 8 and below 64 
    minPasswordLength = 8
    maxPasswordLength = 64

    # Validate the length must be equal/more than 8 character
    if len(password) < minPasswordLength:
        error = 'Your password length must be at least 8 characters.'
        return [False, error]

    # Validate the length must be equal/less than 64 character
    if len(password) > maxPasswordLength:
        error = 'Your password length must be below 64 characters.'
        return [False, error]

    return [True, "Password is validated"]


# Validate password and confirm password
def validate_passwords(password, confirmPassword):
    # Check if the password is empty
    if password == '':
        error = 'Please provide a password.'
        return [False, error]

    # Check if the confirm password is empty
    if confirmPassword == '':
        error = 'Please provide a confirm password.'
        return [False, error]

    # Set password above 8 and below 64 
    minPasswordLength = 8
    maxPasswordLength = 64

     # Validate the length must be equal/more than 8 character
    if len(password) < minPasswordLength:
        error = 'Your password must be at least 8 characters.'
        return [False, error]

    # Validate the length must be equal/less than 64 character
    if len(password) > maxPasswordLength:
        error = 'Your password must be below 64 characters.'
        return [False, error]

    # Validate the password and confirm password matches
    if (password != confirmPassword):
        error = 'Password and confirm password does not match.'
        return [False, error]

    return [True, "Password is validated"]
