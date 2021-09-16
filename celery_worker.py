from monolithic import celery, create_app, init_celery

app = create_app()
celery = init_celery(app)

celery.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'monolithic.tasks.data.print_hello',
        'schedule': 30.0,
        # 'args': (16, 16)
    },
}