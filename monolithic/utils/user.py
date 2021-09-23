from flask import current_app, render_template, url_for
from werkzeug.utils import redirect
from flask_mail import Message
from flask_login import current_user
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from hashlib import sha1


from monolithic import login_manager, mail
from monolithic.models.users import User
from monolithic.tasks import mail

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def send_auth_email(user):
    confirmation_link = generate_confirmation_link(
        user, url_txt='auth.email_auth_completed_page'
    )

    context = dict(email_addr=user.user_email, confirmation_link=confirmation_link)

    mail.send_email_celery.delay(
        subject='가입 이메일 인증',
        recipient=user.user_email,
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
    secret_key = current_app.config.get('SECRET_KEY')
    return URLSafeTimedSerializer(secret_key=secret_key, salt=None).dumps(data)

def confirm_email_token_status(token):
    serializer = URLSafeTimedSerializer(secret_key=current_app.config.get('SECRET_KEY'), salt=None)
    max_age = current_app.config.get('SECURITY_CONFIRM_EMAIL_WITHIN')
    user, data = None, None
    expired, invalid = False, False

    try:
        data = serializer.loads(token, max_age=max_age)
    except SignatureExpired:
        _, data = serializer.loads_unsafe(token)
        expired = True
    except (BadSignature, TypeError, ValueError):
        invalid = True

    if data:
        user = User.query.filter_by(id=data[0]).one_or_none()

    expired = expired and (user is not None)  # TODO 이게 꼭 필요한가...

    return expired, invalid, user


def is_redis_cache_update_possible():
    return current_user.last_redis_cache_update_at and \
        datetime.now() - current_user.last_redis_cache_update_at < timedelta(hours=current_app.config['REDIS_CACHE_UPDATE_LIMIT_TIME'])