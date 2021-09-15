from hashlib import sha1

from flask import Blueprint, render_template, url_for, redirect, request, session, flash, g, current_app
from flask_login import current_user, login_user, logout_user
from werkzeug import security
from itsdangerous import URLSafeTimedSerializer

from monolithic import db
from monolithic.models.users import User
from monolithic.forms.auth_form import LoginForm, RegisterForm
from monolithic.utils.common import flash_form_errors
from monolithic.utils.user import send_auth_email, confirm_email_token_status


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
            # TODO 이 로직도 not과 else를 쓰지 않는 방식으로 변경할 수 있을 듯
            if not security.check_password_hash(user.password, form.password.data):
                flash('password is wrong')
            else:
                if not user.active:
                    return render_template(f'{NAME}/register_email_info_page.html', user_email=user.user_email)
                login_user(user)
                return redirect(url_for('data.file'))
        else:
            flash('account not exists')
            return redirect(request.path)  # TODO 이게 꼭 필요할 것인가...

    return render_template(f'{NAME}/login.html', form=form)

@bp.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for("index"))

@bp.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('data.file'))

    form = RegisterForm()
    # TODO 먼저 post인지 아닌지 검사하는 것이 필요할 것 같다
    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.user_email.data).first()
        if user:
            flash('User ID is already exsits.')
            return redirect(request.path)
        
        user = User(
            user_email=form.user_email.data,
            password=security.generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        send_auth_email(user)
        return render_template(f'{NAME}/register_email_info_page.html', user_email=form.user_email)
    else:
        flash_form_errors(form)

    return render_template(f'{NAME}/register.html', form=form)


@bp.route("/email/send/<string:user_email>/")
def email_send(user_email):
    user = User.query.filter_by(user_email=user_email).first()
    send_auth_email(user)
    return render_template(f'{NAME}/register_email_info_page.html', user_email=user.user_email)


@bp.route("/email_auth_completed_page/")
def email_auth_completed_page():
    """이메일 인증 완료 페이지"""
    if current_user.is_authenticated:
        return redirect(url_for("data.file"))

    token = request.args.get("token", None)
    user_email=request.args.get('email')
    user = User.query.filter_by(user_email=user_email).first()

    if user and user.active:
        login_user(user)
        return redirect(url_for("data.file"))

    if not token:
        flash('이메일 인증 토큰 정보가 없습니다. 재시도 바랍니다.', 'errors')

    expired, invalid, user = confirm_email_token_status(token)

    if not user or invalid:
        flash('이메일 인증 사용자 정보가 없습니다.', 'errors')
    elif expired:
        flash('이메일 인증 유효기간이 만료되었습니다.', 'errors')
    else:
        user.active = True
        db.session.commit()
        login_user(user)
        

    return render_template(f"{NAME}/email_auth_completed_page.html", user_email=request.args.get('email'))