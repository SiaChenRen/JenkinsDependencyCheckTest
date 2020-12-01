from flask import Blueprint, flash, g, redirect, render_template, request, url_for, escape
from werkzeug.exceptions import abort
import math
from app.auth import login_required
from app.db import get_db


bp = Blueprint("common", __name__)


@bp.route("/", methods=("GET", "POST"))
def index():
    if request.method == "GET":
        # Set default data, 
        # postLimit : number of post per pagination
        # pageNumber : current page number, default set to 0
        postLimit = 15
        pageNumber = 0

        # Check for pagination by retrieving page from get argument
        if "page" in request.args:
            try:
                pageNumber = int(request.args["page"]) -1
            except:
                return render_template("index.html")

        db = get_db()

        numOfPost = db.retrieve_number_of_post()

        numOfPage = math.ceil(numOfPost / postLimit)
        pageRange = countPageRange(pageNumber, numOfPage)

        postList = db.retrieve_post_list(pageNumber, postLimit)

        return render_template("index.html",
        data=postList,
        currentPage = pageNumber+1,
        startRange = pageRange.get("start"), 
        endRange = pageRange.get("end"),
        postLimit = postLimit,
        postNumber=numOfPost)
    return render_template("index.html")


def countPageRange(page, pageCount):
    start = page-2
    end = page+2

    if(end > pageCount):
        start -= (end-pageCount)
        end = pageCount

    if(start <= 0):
        end += ((start-1)*(-1))
        start = 1

    if (end > pageCount):
        end = pageCount

    return {"start": start, "end": end}
