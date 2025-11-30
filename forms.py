from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateTimeField, DateField, TimeField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PatientRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Full Name', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Username already exists')

class DoctorRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Full Name', validators=[DataRequired()])
    specialization = StringField('Specialization', validators=[DataRequired()])
    submit = SubmitField('Add Doctor')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Username already exists')

class AppointmentForm(FlaskForm):
    appointment_datetime = DateTimeField('Appointment Date & Time', validators=[DataRequired()], format='%Y-%m-%d %H:%M')
    submit = SubmitField('Book Appointment')

class TreatmentForm(FlaskForm):
    diagnosis = TextAreaField('Diagnosis', validators=[DataRequired()])
    prescriptions = TextAreaField('Prescriptions', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Save Treatment')

class AvailabilityForm(FlaskForm):
    date = DateField(
        'Date', 
        validators=[DataRequired()],
        format='%Y-%m-%d'
    )
    start_time = TimeField(
        'Start Time', 
        validators=[DataRequired()],
        format='%H:%M'
    )
    end_time = TimeField(
        'End Time', 
        validators=[DataRequired()],
        format='%H:%M'
    )
    submit = SubmitField('Add Availability')

