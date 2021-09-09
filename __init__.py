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

celery = Celery(__name__, broker="redis://localhost:6379")

def create_app(config=None):
    app = Flask(__name__)
    
    from .configs import Config
    app.config.from_object(Config())

    """ === Database Init === """
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    login_manager.init_app(app)
    mail.init_app(app)

    from monolithic.models.users import User
    # 아래 구문을 주석처리하면 Exception: Missing user_loader or request_loader. 에러 발생
    # load_user를 정의하였더라도 이것이 메모리에 올라와있지 않으면 이와 같은 에러 발생함. 
    from monolithic.utils.user import load_user
    
    @app.route("/")
    def index():
        return render_template('index.html')

    @login_required
    @app.route("/mypage/")
    def mypage():
        if current_user.is_authenticated:
            return f"<h1>Welcome {current_user.user_email}</h1>"
        return redirect(url_for('auth.login'))
    
    @app.route("/email_auth_completed_page/")
    def email_auth_completed_page():
        return render_template("email_auth_completed_page.html")

    from monolithic.routes import auth, data

    app.register_blueprint(auth.bp)
    app.register_blueprint(data.bp)

    celery.conf.update(app.config)
    
    return app
