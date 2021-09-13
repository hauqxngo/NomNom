from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional
from wtforms.widgets.core import Option

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired()])
    password = PasswordField('New Password', validators=[InputRequired(), Length(min=6)])


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    

class RecipeForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    source = StringField('Source URL', validators=[Optional()])
    ingredients = TextAreaField('Ingredients', validators=[Optional()])
    directions = TextAreaField('Directions', validators=[Optional()])
    image_url = StringField('Image URL', validators=[Optional()])
    leftovers = BooleanField('Leftovers?', validators=[Optional()])


