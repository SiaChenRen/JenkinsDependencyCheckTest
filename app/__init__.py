import os

from flask import Flask, g
from flask_wtf.csrf import CSRFProtect


#create CSRF protection
csrf = CSRFProtect()

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    environment_configuration = os.getenv(
        'CONFIGURATION_SETUP', 'ProductionConfig')
    app.config.from_object('config.' + environment_configuration)

    # Init items
    csrf.init_app(app)
    
    # register the database commands
    from app import db

    db.init_app(app)

    # apply the blueprints to the app
    from app import auth, common, account, posts, administrator, moderator

    app.register_blueprint(auth.bp)
    app.register_blueprint(common.bp)
    app.register_blueprint(account.bp)
    app.register_blueprint(posts.bp)
    app.register_blueprint(moderator.bp)
    app.register_blueprint(administrator.bp)

    # default url for site
    app.add_url_rule("/", endpoint="index")

    return app
