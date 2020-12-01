import functools
import sys
import re
import io
import os

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, escape
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from app.db import get_db
from app.auth import login_required
from app.logging import log_user_action


bp = Blueprint("post", __name__, url_prefix="/post")


@bp.route("/", methods=("GET", "POST"))
def get_post():
    if request.method == "GET":
        # Retrieve and sanitize form variable
        if "post" in request.args:
            post_id = str(request.args["post"].strip())
        else:
            error = "Error in retrieving the post."
            return render_template("index.html", error=error)

         # Validate if post is empty
        if post_id == '':
            error = "Error in retrieving the post."
            return render_template("index.html", error=error)

        # Get Database
        db = get_db()

        # Retrieve post through postId
        post = db.retrieve_post(post_id)
        session["post_author"] = post.post_author
        return render_template("post/single-post.html", data=post)
    return render_template("index.html")


@bp.route("/search", methods=("GET", "POST"))
def search_post():
    if request.method == "POST":
        # Check if the input is empty
        try:
            searchTerm = str(escape(request.form["search"].strip()))
        except:
            flash("Error in searching the post.", "search_error")
            return redirect(url_for("index"))

        # Validate search term
        if searchTerm == '':
            flash("Error in searching the post.", "search_error")
            return redirect(url_for("index"))
  
        pattern = "^[ A-Za-z0-9~!@#$%^&*\\(\\)_+-=""'':;,<>.?/~`]+$"
        if (bool(re.match(pattern, searchTerm)) != True):
            flash ("Letters, numbers, and common symbols only.", "search_error")
            return redirect(url_for("index"))

        # Get Database
        db = get_db()

        # Search data in database
        post = db.search_post(searchTerm)
        return render_template("post/search-post.html", data=post, searchTerm=searchTerm)
    return render_template("post/search-post.html")


@bp.route("/create-post", methods=("GET", "POST"))
@login_required
@log_user_action
def create_post():
    if request.method == "POST":

        # Retrieve post content
        post_title = str(escape(request.form["post-title"].strip()))
        post_description = str(
            escape(request.form["post-description"].strip()))
        post_content = str(escape(request.form["post-content"].strip()))

        # Validate post title
        if post_title == "":
            return render_template("post/create-post.html", error="Please enter the education material title.")

        regex = "^[ A-Za-z0-9~!@#$%^&*\\(\\)_+-=""'':;,<>.?/~`]+$"
        if not re.match(regex, post_title):
            error = 'Letters, numbers, and common symbols only please.'
            return render_template("post/create-post.html", error=error)

        maxLength = 255
        if len(post_title) > maxLength:
            return render_template("post/create-post.html", error="The number of character in post title exceed 255 character.")
        # Get Database
        db = get_db()

        # Create post in mysql and mynosql
        create_post_result = db.create_post(post_title, post_description, post_content)
        if create_post_result[0] != True:
            return render_template("post/create-post.html", error=create_post_result[1])
        
        return render_template("post/create-post.html", info=create_post_result[1])
    if request.method == "GET":
        return render_template("post/create-post.html")


@bp.route("/scan-document", methods=("GET", "POST"))
@login_required
@log_user_action
def scan_document():
    if request.method == "POST":
        from app.ocr import Tesseract
        
        allow_ext = ['.jpg', '.jpeg', '.png']
        concat_text = ""

        # Retrieve file content
        try:
            file_list = request.files
        except Exception as e:
            print(e)
            return concat_text

        ocr = Tesseract()
        # Iterate the request file
        for key, file in file_list.items():

            # Retrieve filename through secure_filename
            filename = secure_filename(file.filename)
            # Check if the filename is not none
            if filename != '':

                # Validate file extension (png, jpeg, jpg)
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in allow_ext:
                    return concat_text
                # Input file into bufferedreader, sent to OCR
                file.name = filename
                file = io.BufferedReader(file)
                result = ocr.send_ocr(file)
                # Read the response valid, concat text for multiple file ocr
                if result.get("response") == True:
                    concat_text += escape(str(result.get("data").strip()))

        return concat_text
    if request.method == "GET":
        return "Error in retrieving"
