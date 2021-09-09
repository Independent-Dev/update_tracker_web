from flask import current_app, render_template, url_for
from flask_mail import Message
from flask_login import current_user
from itsdangerous import URLSafeTimedSerializer

from hashlib import sha1


from monolithic import login_manager, mail
from monolithic.models.users import User
from monolithic.tasks import mail

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def send_auth_email():
    confirmation_link = generate_confirmation_link(
        current_user, url_txt='email_auth_completed_page'
    )

    context = dict(email_addr=current_user.user_email, confirmation_link=confirmation_link)

    mail.send_email_celery.delay(
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
