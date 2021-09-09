from flask import current_app, render_template
from flask_mail import Message
from monolithic import mail, celery

@celery.task
def send_email_celery(subject, recipient, template, **context):
    msg = dict(subject=subject,
               sender=current_app.config['SECURITY_EMAIL_SENDER'],
               recipients=[recipient])
    msg['body'] = render_template('%s.txt' % template, **context)
    msg['html'] = render_template('%s.html' % template, **context)

    try:
        current_app.logger.info("메일 수신자: '{}' 에게 제목: '{}' 의 메일 발송 시도".format(recipient, subject))

        flask_msg = Message(**msg)
        mail.send(flask_msg)
    except Exception as e:
        current_app.logger.error(e)
    else:
        current_app.logger.info("메일 수신자: '{}' 에게 제목: '{}' 의 메일 발송 성공".format(recipient, subject))