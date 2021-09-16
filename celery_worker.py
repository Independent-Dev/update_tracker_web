from monolithic import celery, create_app, init_celery
from celery.schedules import crontab

app = create_app()
celery = init_celery(app)

celery.conf.beat_schedule = {
    'update_redis_cache': {
        'task': 'monolithic.tasks.data.update_redis_cache',
        'schedule': crontab(hour='*/6')  # 6시간마다 캐시 갱신 
    },
}