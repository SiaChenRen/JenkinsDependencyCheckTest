import functools
import sys
import re

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, escape
from werkzeug.security import check_password_hash, generate_password_hash

from app.auth import login_required
from app.db import get_db
from app.logging import log_user_action

bp = Blueprint("account", __name__, url_prefix="/account")

@bp.route("/profile", methods=("GET", "POST"))
@login_required
@log_user_action
def profile():
    if request.method == "POST":
        # Retrieve and sanitize form variable
        try:
            submitType = str(escape(request.form["submit"].strip()))

            if submitType == "Change Email" :
                email = str(escape(request.form["email"].strip()))
            elif submitType == "Change Password":
                oldPassword = str(escape(request.form["oldpassword"].strip()))
                newPassword = str(escape(request.form["password"]).strip())
                newConfirmPassword = str(escape(request.form["confirmpassword"].strip()))
            else:
                raise
        except:
            error = "Error in changing the account information"
            return render_template("account/profile.html", error=error)

        # Get Database
        db = get_db()

        # Trigger methods to change email
        if submitType == "Change Email":

            # Validate the new email if it meet the requirement of Not Empty,
            # No existing account linked, have a "@" and "."
            validateStatus = validate_email(email)
            if validateStatus[0] != True:
                return render_template("account/profile.html", emailError=validateStatus[1])

            # Update the email address
            changeEmailResult = db.update_email(session["user"], validateStatus[1])
            if changeEmailResult == True:
                session.clear()
                flash("Email updated. Please login again.")
                return redirect(url_for("auth.login"))
            return render_template("account/profile.html", emailError="Failed to change the email address.")



        # Trigger methods to update email
        if submitType == "Change Password":

            # Validate the current password if valid, new password and confirm password
            # length on between 8 and 64 character
            validateStatus = validate_password(oldPassword, newPassword, newConfirmPassword)
            if validateStatus[0] != True:
                return render_template("account/profile.html", passwordError=validateStatus[1])

            # Update the password
            changePasswordResult = db.update_password(session["user"], validateStatus[1])
            if changePasswordResult == True:
                session.clear()
                flash("Password updated. Please login again.")
                return redirect(url_for("auth.login"))
            return render_template("account/profile.html", passwordError="Failed to change the password.")


    if request.method == "GET":
        # Get Database
        db = get_db()

        # Retrieve and display user email for placeholder
        userEmail = db.retrieve_email(session["user"])

        if userEmail[0] == True:
            return render_template("account/profile.html", data=userEmail[1])
        return render_template("account/profile.html", emailError=userEmail[1])

    return render_template("account/profile.html")


@bp.route("/post", methods=("GET", "POST"))
@login_required
def account_post():
    if request.method == "GET":
        # Get Database
        db = get_db()

        # Retrieve all user post
        post_data = db.retrieve_account_post_list(session["user"])

        return render_template("account/post.html", data = post_data)

    return render_template("account/post.html")


@bp.route("/delete-post", methods=("GET", "POST"))
@login_required
@log_user_action
def delete_post():
    if request.method == "GET":
         # Retrieve and sanitize form variable
        if "post" in request.args:
            postID = request.args["post"].strip()
        else:
            flash("Error in deleting Post.", "error")
            return redirect(url_for("account.account_post"))

        # Get Database
        db = get_db()

        # Delete post
        deletePostResult = db.delete_post(session["user"], postID)

        if deletePostResult[0] is True:
            flash(deletePostResult[1], "success")
            return redirect(url_for("account.account_post"))

        flash(deletePostResult[1], "error")
        return redirect(url_for("account.account_post"))


    return redirect(url_for("account.account_post"))


@bp.route("/edit-post", methods=("GET", "POST"))
@login_required
@log_user_action
def edit_post():
    if request.method == "GET":

         # Retrieve and sanitize form variable
        if "post" in request.args:
            postID = request.args["post"].strip()
        else:
            return redirect(url_for("account.account_post"))

        # Get Database
        db = get_db()

        # Retrieve post by postId
        post = db.retrieve_post(postID)
        return render_template("account/edit-post.html", data = post)

    if request.method == "POST":

        # Retrieve and sanitize form variable
        try:
            postTitle = escape(request.form["post-title"].strip())
            postDescription =  escape(request.form["post-description"].strip())
            postID = request.form["post-id"].strip()
        except:
             render_template("account/edit-post.html", error = "Error in updating post")

        # Get Database
        db = get_db()

        # Retrieve post by postId
        result = db.update_post(session["user"], postID, postTitle, postDescription)
        if result[0] is not False:
            flash(result[1], "success")
            return redirect(url_for("account.account_post"))
        return render_template("account/edit-post.html", error = result[1])

    return redirect(url_for("account.account_post"))


@bp.route("/direct-message", methods=("GET", "POST"))
@login_required
def direct_message():
    if request.method == "GET":
        # Retrieve and sanitize form variable
        account_id = 0
        if "user" in request.args:
            account_id = request.args["user"]

        # Get Database
        db = get_db()

        # Retrieve message with user account id and recipient account id
        message_list = []
        if account_id != 0:
            message_list = db.retrieve_messages(session["user"], account_id)


        # Retrieve previous conversation list with user account id
        conversation_result = db.retrieve_conversation_list(session["user"])

        # Retrieve previous conversation list with user account id
        conversation_list = []
        for conversation in conversation_result[1]:
            data_account1_id = conversation.get("account1_id")
            data_account2_id = conversation.get("account2_id")
            if data_account1_id not in conversation_list and data_account1_id != session["user"]:
                conversation_list.append(data_account1_id)
            if data_account2_id not in conversation_list and data_account2_id != session["user"] :
                conversation_list.append(data_account2_id)

        # Retrieve previous conversation list with user account id
        if conversation_result[0] == False:
            return render_template("account/direct-message.html", error="Error to retrieve conversation.", message=message_list)

        return render_template("account/direct-message.html", conversation=conversation_list, message=message_list, user=account_id)


    if request.method == "POST":
        # Retrieve and sanitize form and session variable
        try:
            message = escape(request.form["post-message"].strip())
            account_id = request.form["user"].strip()
        except:
           return redirect(url_for("account.direct_message", user=account_id))

         # Get Database
        db = get_db()

        # Db send message
        send_message_result = db.send_message(session["user"], account_id, message)
        return redirect(url_for("account.direct_message", user=account_id))
    return render_template("account/direct-message.html")




# Helper function

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

    # Check for existing email account
    db = get_db()
    checkEmailStatus = db.check_existing_email(email)
    if checkEmailStatus == True:
        error = 'Invalid email address.'
        return [False, error]

    return [True, email]


def validate_password(oldPassword, newPassword, confirmPassword):
    # Check if the newPassword and confirmPassword is the same
    if newPassword != confirmPassword:
        error = 'Password does not match'
        return [False, error]
    # Check if the inputs is empty
    if request.form["oldpassword"] == '':
        error = 'Please provide current password.'
        return render_template("account/profile.html", passwordError=error)

    if request.form["password"] == '':
        error = 'Please provide a new password.'
        return render_template("account/profile.html", passwordError=error)

    if request.form["confirmpassword"] == '':
        error = 'Please provide confirm password.'
        return render_template("account/profile.html", passwordError=error)

    # Set password above 8 and below 64
    minPasswordLength = 8
    maxPasswordLength = 64

    # Validate the new password length must be equal/more than 8 character
    if len(newPassword) < minPasswordLength:
        error = 'Your new password length must be at least 8 characters.'
        return [False, error]

    # Validate the length must be equal/less than 64 character
    if len(newPassword) > maxPasswordLength:
        error = 'Your new password length must be below 64 characters.'
        return [False, error]

    # Check if the current password is valid
    db = get_db()
    checkPasswordStatus = db.check_current_password(session["user"], oldPassword)
    if checkPasswordStatus == True:
        return [True, newPassword]

    error = 'Invalid password.'
    return [False, error]


