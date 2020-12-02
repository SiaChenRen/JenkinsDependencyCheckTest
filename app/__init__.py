import os

from flask import Flask



def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    # apply the blueprints to the app
    from app import common

    app.register_blueprint(common.bp)

    # default url for site
    app.add_url_rule("/", endpoint="index")

    return app
