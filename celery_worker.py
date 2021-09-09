from monolithic import celery, create_app, init_celery

app = create_app()
celery = init_celery(app)