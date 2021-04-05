from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo


# form for register page
class RegistrationForm(FlaskForm):
    username = StringField("Username",
                            validators=[DataRequired()]) # return error if data is null
    password = PasswordField("Password",
                            validators=[DataRequired()]) # return error if data is null
    confirm_password = PasswordField("Confirm Password",
                            validators=[DataRequired(), EqualTo("password")]) # return error if data is null, or data is different from password
    submit = SubmitField("Register")    


# form for login page
class LoginForm(FlaskForm):
    username = StringField("Username",
                            validators=[DataRequired()]) # return error if data is null
    password = PasswordField("Password",
                            validators=[DataRequired()]) # return error if data is null
    submit = SubmitField("Login")    