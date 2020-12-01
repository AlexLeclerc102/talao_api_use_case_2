from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    did = db.Column(db.String(100))
    username = db.Column(db.String(100))
    pending_certificates = db.relationship('Pending_certificate', backref='User', lazy=True)

class Pending_certificate(db.Model):
    __tablename__ = 'Pending_certificate'
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    title = db.Column(db.String(100))
    description = db.Column(db.String(10000))
    start_date  = db.Column(db.String(10))
    end_date  = db.Column(db.String(10))
    message = db.Column(db.String(1000))
