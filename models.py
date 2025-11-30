from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Optional
from extensions import db
from flask_login import UserMixin

ROLE_ADMIN = 'admin'
ROLE_DOCTOR = 'doctor'
ROLE_PATIENT = 'patient'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False)

    doctor_profile = db.relationship('Doctor', backref='user', uselist=False)
    patient_profile = db.relationship('Patient', backref='user', uselist=False)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)

class EditDoctorForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Optional()])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password', message='Passwords must match'), Optional()])
    name = StringField('Full Name', validators=[DataRequired()])
    specialization = StringField('Specialization', validators=[DataRequired()])
    submit = SubmitField('Update Doctor')

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    specialization = db.Column(db.String(120), nullable=False)
    availabilities = db.relationship('DoctorAvailability', backref='doctor', cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', backref='doctor', cascade='all, delete-orphan')
    treatments = db.relationship('TreatmentRecord', back_populates='doctor', cascade='all, delete-orphan')

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    contact = db.Column(db.String(50))

    appointments = db.relationship('Appointment', backref='patient', cascade='all, delete-orphan')

    treatments = db.relationship('TreatmentRecord', back_populates='patient', cascade='all, delete-orphan')

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Booked')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reschedule_count = db.Column(db.Integer, nullable=False, default=0)

    treatments = db.relationship('TreatmentRecord', back_populates='appointment', cascade='all, delete-orphan')

    __table_args__ = (db.UniqueConstraint('doctor_id', 'appointment_datetime', name='uq_doctor_datetime'),)

class DoctorAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

class TreatmentRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=True)
    diagnosis = db.Column(db.Text)
    prescriptions = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', back_populates='treatments')
    doctor = db.relationship('Doctor', back_populates='treatments')
    appointment = db.relationship('Appointment', back_populates='treatments')

