from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateTimeField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import Voter, Election, Candidate
from datetime import datetime
from wtforms.fields import DateTimeLocalField

class RegistrationForm(FlaskForm):
    """Form for voter registration"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    date_of_birth = DateTimeField('Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    voter_id = StringField('Voter ID', validators=[DataRequired(), Length(min=5, max=20)])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        voter = Voter.query.filter_by(username=username.data).first()
        if voter:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        voter = Voter.query.filter_by(email=email.data).first()
        if voter:
            raise ValidationError('Email already registered. Please use a different one.')
    
    def validate_voter_id(self, voter_id):
        voter = Voter.query.filter_by(voter_id=voter_id.data).first()
        if voter:
            raise ValidationError('Voter ID already registered.')
    
    def validate_date_of_birth(self, date_of_birth):
        if date_of_birth.data:
            # Convert to date if it's a datetime
            dob = date_of_birth.data
            if isinstance(dob, datetime):
                dob = dob.date()
            if dob > datetime.now().date():
                raise ValidationError('Date of birth cannot be in the future.')

class LoginForm(FlaskForm):
    """Form for voter login"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ElectionForm(FlaskForm):
    """Form for creating elections"""
    title = StringField('Election Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Length(max=1000)])
    start_date = DateTimeLocalField('Start Date', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    end_date = DateTimeLocalField('End Date', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    submit = SubmitField('Create Election')
    
    def validate_end_date(self, end_date):
        if end_date.data and self.start_date.data and end_date.data <= self.start_date.data:
            raise ValidationError('End date must be after start date.')
    
    def validate_start_date(self, start_date):
        if start_date.data and start_date.data < datetime.now():
            raise ValidationError('Start date cannot be in the past.')

class CandidateForm(FlaskForm):
    """Form for adding candidates to elections"""
    name = StringField('Candidate Name', validators=[DataRequired(), Length(max=100)])
    party = StringField('Party', validators=[Length(max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    submit = SubmitField('Add Candidate')

class EditCandidateForm(FlaskForm):
    """Form for editing candidates"""
    name = StringField('Candidate Name', validators=[DataRequired(), Length(max=100)])
    party = StringField('Party', validators=[Length(max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    submit = SubmitField('Update Candidate')

class VoteForm(FlaskForm):
    """Form for casting votes"""
    candidate = SelectField('Select Candidate', coerce=str, validators=[DataRequired()])
    submit = SubmitField('Cast Vote')
    
    def __init__(self, candidates=None, *args, **kwargs):
        super(VoteForm, self).__init__(*args, **kwargs)
        if candidates:
            self.candidate.choices = [(c.id, f"{c.name} ({c.party})" if c.party else c.name) for c in candidates]

class AdminForm(FlaskForm):
    """Form for admin actions"""
    action = SelectField('Action', choices=[
        ('mine', 'Mine Pending Transactions'),
        ('validate', 'Validate Blockchain'),
        ('export', 'Export Blockchain Data')
    ], validators=[DataRequired()])
    submit = SubmitField('Execute Action')