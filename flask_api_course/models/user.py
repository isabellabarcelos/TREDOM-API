from db import db


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String(256), unique=False, nullable=False)

class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    user = db.relationship('UserModel', backref=db.backref('patient', uselist=False))
    name = db.Column(db.String(255), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    weight = db.Column(db.Numeric(5, 2), nullable=False)
    race = db.Column(db.String(20), nullable=False)
    height = db.Column(db.Numeric(5, 2), nullable=False)

class HealthProfessional(db.Model):
    __tablename__ = "health_professionals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    user = db.relationship('UserModel', backref=db.backref('health_professional', uselist=False))
    name = db.Column(db.String(255), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    medical_register = db.Column(db.String(20), nullable=False)