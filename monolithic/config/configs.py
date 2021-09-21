import os, datetime


class Config:
    """Flask Config"""
    SESSION_PERMANENT = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    POSSIBLE_FILE_EXTENSION = ["txt"]
    
    # Flask-Mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    SECURITY_CONFIRM_EMAIL_WITHIN = datetime.timedelta(days=1).total_seconds()

    # celery
    PYPI_SEARCH_URL_FORMAT = "https://pypi.python.org/pypi/{}/json"

class ProductionConfig(Config):
    SECRET_KEY = '3961fe7dd81b4dae8970b81ed3f47d30'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@db-server/monolithic'
    CELERY_BROKER_URL = 'redis://redis-server:6379'
    REDIS_HOST = 'redis-server'

    
class TestConfig(Config):
    SECRET_KEY = 'secret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    CELERY_BROKER_URL = 'redis://localhost:6379'
    REDIS_HOST = 'localhost'

