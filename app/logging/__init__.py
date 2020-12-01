import time
from functools import wraps
from flask import current_app as app, session

from app.db import get_db


# Decorator to redirects anonymous or invalid users to the login page.
def log_user_action(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        db = get_db()
        data = {}

        data["user"] = session["user"]
        data["role"] = session["role"]
        data["timestamp"] = time.time()
        data["action"] = function.__name__

        db.log_entry(data)

        return function(*args, **kwargs)

    return wrapper