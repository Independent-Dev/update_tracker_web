from hashlib import sha1

from flask import Blueprint, render_template, url_for, redirect, request, session, flash, g, current_app
from flask_login import current_user, login_user, logout_user
from werkzeug import security
from itsdangerous import URLSafeTimedSerializer

from monolithic import db
from monolithic.models.users import User
from monolithic.forms.auth_form import LoginForm, RegisterForm
from monolithic.utils.common import flash_form_errors
from monolithic.utils.user import send_email_celery


NAME = 'auth'
bp = Blueprint(NAME, __name__, url_prefix=f'/{NAME}')

def send_auth_email():
    confirmation_link = generate_confirmation_link(
        current_user, url_txt='email_auth_completed_page'
    )

    context = dict(email_addr=current_user.user_email, confirmation_link=confirmation_link)

    send_email_celery(
        subject='가입 이메일 인증',
        recipient=current_user.user_email,
        template='email/send_auth_email',
        **context
    )

def generate_confirmation_link(user, url_txt):
    token = generate_confirmation_token(user)
    return url_for(url_txt, token=token, email=user.user_email, _external=True)

def generate_confirmation_token(user):
    """Generates a unique confirmation token for the specified user.

    :param user: The user to work with
    """
    data = [str(user.id), sha1(user.user_email.encode('utf-8')).hexdigest()]
    from monolithic import create_app
    secret_key = current_app.config.get('SECRET_KEY')
    return URLSafeTimedSerializer(secret_key=secret_key, salt=None).dumps(data)


@bp.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('mypage'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.user_email.data).first()
        if user:
            if not security.check_password_hash(user.password, form.password.data):
                flash('password is wrong')
            else:
                login_user(user)
                return redirect(url_for('mypage'))
        else:
            flash('account not exists')
            return redirect(request.path)

    return render_template(f'{NAME}/login.html', form=form)

@bp.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for("index"))

@bp.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    # todo 먼저 post인지 아닌지 검사하는 것이 필요할 것 같다
    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.user_email.data).first()
        if user:
            flash('User ID is already exsits.')
            return redirect(request.path)
        else:
            user = User(
                user_email=form.user_email.data,
                password=security.generate_password_hash(form.password.data)
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            send_auth_email()
            # login_user(user)
        return redirect(url_for('index'))
    else:
        flash_form_errors(form)
    
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    return render_template(f'{NAME}/register.html', form=form)