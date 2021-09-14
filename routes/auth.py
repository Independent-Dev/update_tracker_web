from hashlib import sha1

from flask import Blueprint, render_template, url_for, redirect, request, session, flash, g, current_app
from flask_login import current_user, login_user, logout_user
from werkzeug import security
from itsdangerous import URLSafeTimedSerializer

from monolithic import db
from monolithic.models.users import User
from monolithic.forms.auth_form import LoginForm, RegisterForm
from monolithic.utils.common import flash_form_errors
from monolithic.utils.user import send_auth_email


NAME = 'auth'
bp = Blueprint(NAME, __name__, url_prefix=f'/{NAME}')


@bp.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('data.file'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.user_email.data).first()
        if user:
            if not security.check_password_hash(user.password, form.password.data):
                flash('password is wrong')
            else:
                login_user(user)
                return redirect(url_for('data.file'))
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
        return redirect(url_for('data.file'))
    else:
        flash_form_errors(form)
    
    if current_user.is_authenticated:
        return redirect(url_for('data.file'))

    return render_template(f'{NAME}/register.html', form=form)

@bp.route("/email_auth_completed_page/")
def email_auth_completed_page():
    return render_template("email_auth_completed_page.html")