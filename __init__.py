import os

from flask import Flask, render_template, url_for
from werkzeug.utils import redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, current_user
from flask_mail import Mail, Message

from celery import Celery

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

celery = Celery(__name__)

def create_app(config=None):
    app = Flask(__name__)
    
    from .configs import ProductionConfig, TestConfig
    
    if os.environ.get('FLASK_ENV', '') == "development":
        config = TestConfig()
    else:
        config = ProductionConfig()

    app.config.from_object(config)


    """ === Database Init === """
    db.init_app(app)

    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    from monolithic.models.users import User
    # 아래 구문을 주석처리하면 Exception: Missing user_loader or request_loader. 에러 발생
    # load_user를 정의하였더라도 이것이 메모리에 올라와있지 않으면 이와 같은 에러 발생함. 
    from monolithic.utils.user import load_user
    from monolithic.routes import auth, data

    app.register_blueprint(auth.bp)
    app.register_blueprint(data.bp)

    celery.conf.update(app.config)

    @app.route("/")
    def index():
        return redirect(url_for("data.file"))
    
    @app.route("/intro/")
    def intro():
        return render_template("intro.html")
    
    return app


def init_celery(app):
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
