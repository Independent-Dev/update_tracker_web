from flask import current_app, render_template
from flask_mail import Message
from monolithic import mail, celery
from monolithic.tasks.mail import send_email_celery
from monolithic.utils.data import UpdateTracker, Redis


@celery.task
def analyze_and_report_package_data(package_info, user_email):
    update_tracker = UpdateTracker(package_info, user_email)
    update_tracker.report_package_info()

@celery.task
def update_redis_cache():
    current_app.logger.info("update_redis_cache 메소드 시작")
    redis = Redis()

    current_app.logger.info("fetch_updated_package_data 시작")

    for package_name in redis.get_keys():
        try:
            redis.fetch_updated_package_data(package_name)
        except Exception as e:
            current_app.logger.debug(f"package_name: {package_name}, error: {e}")

    current_app.logger.info("fetch_updated_package_data 완료")
    redis.cache_update()
    
    current_app.logger.info("update_redis_cache 메소드 완료")
    