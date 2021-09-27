import os

from flask import Flask, render_template, url_for
from werkzeug.utils import redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from flask_mail import Mail

from celery import Celery

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

celery = Celery(__name__)


def create_app(config=None):
    app = Flask(__name__)

    from monolithic.config import configs, private

    if os.environ.get('FLASK_ENV', '') == "development":
        config = configs.TestConfig()
    else:
        config = configs.ProductionConfig()

    app.config.from_object(config)
    app.config.from_object(private.PrivateConfig())

    """ === Database Init === """
    db.init_app(app)

    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)
    mail.init_app(app)

    from monolithic.models.users import User
    from monolithic.utils.user import load_user
    login_manager.init_app(app)

    from monolithic.routes import auth, data

    app.register_blueprint(auth.bp)
    app.register_blueprint(data.bp)

    celery.conf.update(app.config)
    celery.conf.broker_url = app.config["CELERY_BROKER_URL"]

    @app.route("/")
    def index():
        return redirect(url_for("data.file"))

    @app.route("/intro/")
    def intro():
        return render_template("intro.html")

    # TODO 공통 예외 처리 필요함.

    return app


def init_celery(app):
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
