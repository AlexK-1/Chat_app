from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, PasswordField, TextAreaField, SubmitField, SelectField, EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class LogInForm(FlaskForm):
    username = StringField("Username: ", validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField("Password: ", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Log in")

class SignUpForm(FlaskForm):
    username = StringField("Username: ", validators=[DataRequired(), Length(min=4, max=20)])
    email = EmailField("Email: ", validators=[DataRequired(), Email(), Length(min=5, max=320)])
    password = PasswordField("Password: ", validators=[DataRequired(), Length(min=8, max=100)])
    password2 = PasswordField("Password (again): ", validators=[DataRequired(), Length(min=8, max=100),
                                                                EqualTo("password", message="Passwords don't match")])
    submit = SubmitField("Register")

class PostForm(FlaskForm):
    text = TextAreaField("", validators=[DataRequired()])
    submit = SubmitField("Send")
