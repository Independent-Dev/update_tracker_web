from flask import current_app, render_template
from flask_mail import Message
from monolithic import mail, celery
from monolithic.tasks.mail import send_email_celery
from monolithic.utils.data import UpdateTracker

@celery.task
def analyze_and_report_package_data(package_info, user_email):
    update_tracker = UpdateTracker(package_info, user_email)
    update_tracker.report_package_info()