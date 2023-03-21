import wtforms
from flask_login import current_user
from flask_wtf import FlaskForm, file
from wtforms.validators import (DataRequired, Email, EqualTo, InputRequired,
                                Length, Regexp, ValidationError)

from main_code.models import User


class register_form(FlaskForm):
    username = wtforms.StringField(
        validators=[
            InputRequired(),
            Length(3, 20, message="Please provide a valid name"),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Usernames must have only letters, " "numbers, dots or underscores",
            ),
        ],
        label='Username'
    )
    email = wtforms.StringField(validators=[InputRequired(), Email(), Length(1, 64)], label='Email')
    pwd = wtforms.PasswordField(validators=[InputRequired(), Length(8, 72)], label='Password')
    cpwd = wtforms.PasswordField(
        validators=[
            InputRequired(),
            Length(8, 72),
            EqualTo("pwd", message="Passwords must match !"),
        ],
        label='Repeat password'
    )
    submit = wtforms.SubmitField('Sign Up')


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username already exists. Try another one')

    def validate_email(self, email):
        user = User.query.filter_by(username=email.data).first()
        if user:
            raise ValidationError('That email already exists. Try another one')


class login_form(FlaskForm):
    email = wtforms.StringField(validators=[InputRequired(), Email(), Length(1, 64)], label='Email')
    pwd = wtforms.PasswordField(validators=[InputRequired(), Length(min=8, max=72)], label='Password')
    submit = wtforms.SubmitField('Sign in')


class Update_account_form(FlaskForm):
    username = wtforms.StringField(
        validators=[
            InputRequired(),
            Length(3, 20, message="Please provide a valid name"),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Usernames must have only letters, " "numbers, dots or underscores",
            ),
        ],
        label='Username'
    )
    email = wtforms.StringField(validators=[InputRequired(), Email(), Length(1, 64)], label='Email')
    image = file.FileField(validators=[file.FileAllowed(['jpg', 'png'])], label="Update picture")
    submit = wtforms.SubmitField('Update profile')


    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('New username shall be unique')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(username=email.data).first()
            if user:
                raise ValidationError('New email shall be unique')


class PostForm(FlaskForm):
    title = wtforms.StringField(label='Title', validators=[DataRequired()])
    content = wtforms.TextAreaField(label='Content', validators=[DataRequired()])
    submit = wtforms.SubmitField('Create post')
