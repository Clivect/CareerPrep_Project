from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from models import User


class JobSearchForm(FlaskForm):
    query = StringField('Search Jobs', validators=[DataRequired()])
    submit = SubmitField('Search')

class JobApplicationForm(FlaskForm):
    company = StringField('Company', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    status = SelectField('Status', choices=[('applied', 'Applied'), ('in_progress', 'In Progress'), ('interview', 'Interview'), ('offer', 'Offer'), ('rejected', 'Rejected')], validators=[DataRequired()])
    submit = SubmitField('Add Application')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ResumeBuilderForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=15)])
    summary = TextAreaField('Summary', validators=[DataRequired(), Length(max=1000)])
    experience = TextAreaField('Experience', validators=[DataRequired(), Length(max=2000)])
    education = TextAreaField('Education', validators=[DataRequired(), Length(max=1000)])
    skills = TextAreaField('Skills', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Generate Resume')


class MessageForm(FlaskForm):
    content = TextAreaField('Type something...', validators=[DataRequired()])
    submit = SubmitField('Post')

