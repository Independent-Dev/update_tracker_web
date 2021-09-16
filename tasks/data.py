from flask import current_app, render_template
from flask_mail import Message
from monolithic import mail, celery
from monolithic.tasks.mail import send_email_celery
from monolithic.utils.data import UpdateTracker

# @celery.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     # Calls test('world') every 30 seconds
#     sender.add_periodic_task(30.0, print_hello.s('world'), expires=10)

@celery.task
def analyze_and_report_package_data(package_info, user_email):
    update_tracker = UpdateTracker(package_info, user_email)
    update_tracker.report_package_info()

@celery.task
def print_hello():
    current_app.logger.info("hello")