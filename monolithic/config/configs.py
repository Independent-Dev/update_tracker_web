import datetime


class Config:
    """Flask Config"""
    SESSION_PERMANENT = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    POSSIBLE_FILE_EXTENSION = ["txt"]

    REDIS_CACHE_UPDATE_LIMIT_TIME = 2

    # Flask-Mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    SECURITY_CONFIRM_EMAIL_WITHIN = datetime.timedelta(days=1).total_seconds()

    # celery
    PYPI_SEARCH_URL_FORMAT = "https://pypi.python.org/pypi/{}/json"
    REDIS_PACKAGE_NAME_PREFIX = "___"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@db-server/monolithic'
    CELERY_BROKER_URL = 'redis://user:updatetracker@redis-server:6379'
    REDIS_HOST = 'redis-server'
    REDIS_PASSWORD = 'updatetracker'


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    CELERY_BROKER_URL = 'redis://localhost:6379'
    REDIS_HOST = 'localhost'
    REDIS_PASSWORD = None
