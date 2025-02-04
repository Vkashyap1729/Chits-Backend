from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz  # For timezone conversion

# Initialize db object
db = SQLAlchemy()

# Define IST Timezone
IST = pytz.timezone('Asia/Kolkata')


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Integer)
    validated = db.Column(db.Boolean)
    otp = db.Column(db.String(6), nullable=False)
    forgot_opt = db.Column(db.String(6), nullable=True)  # Missing in your model


class Chit(db.Model):
    __tablename__ = 'chit'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    tenure = db.Column(db.Integer, nullable=False)
    noOfPeople = db.Column(db.Integer, nullable=False)
    amountPerMonth = db.Column(db.Float, nullable=False)
    totalAmount = db.Column(db.Float, nullable=False)
    startDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date, nullable=False)
    createdAt = db.Column(
        db.DateTime,
        default=lambda: datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(IST)
    )

class ChitMembers(db.Model):
    __tablename__ = 'chitMembers'
    UniqueCode = db.Column(db.String(255), nullable=False)
    chitId = db.Column(db.Integer, db.ForeignKey('chit.id'), primary_key=True)
    managerId = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    liftedMonth = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)

class ChitManager(db.Model):
    __tablename__ = 'chitManager'

    id = db.Column(db.Integer, primary_key=True)
    chitId = db.Column(db.Integer, db.ForeignKey('chit.id', ondelete='CASCADE'), nullable=False)
    managerId = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    chit = db.relationship('Chit', backref=db.backref('chit_managers', lazy=True, passive_deletes=True))
