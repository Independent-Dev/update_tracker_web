from flask import current_app, render_template
from flask_mail import Message

from monolithic import login_manager, mail
from monolithic.models.users import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def send_email_celery(subject, recipient, template, **context):
    msg = dict(subject=subject,
               sender=current_app.config['SECURITY_EMAIL_SENDER'],
               recipients=[recipient])
    msg['body'] = render_template('%s.txt' % template, **context)
    msg['html'] = render_template('%s.html' % template, **context)

    is_mail_send_success = True  # 메일 발송 성공 여부(Celery 미사용시에만 사용)

    flask_msg = Message(**msg)
    mail.send(flask_msg)

    try:
        current_app.logger.info("메일 수신자: '{}' 에게 제목: '{}' 의 메일 발송 시도".format(recipient, subject))

        flask_msg = Message(**msg)
        mail.send(flask_msg)
    except Exception as e:
        current_app.logger.error(e)
    else:
        current_app.logger.info("메일 수신자: '{}' 에게 제목: '{}' 의 메일 발송 성공".format(recipient, subject))

    return is_mail_send_success