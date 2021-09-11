from monolithic import db
from sqlalchemy import func
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=func.now())
    active = db.Column(db.Boolean(), nullable=False, default=False, server_default='0')
