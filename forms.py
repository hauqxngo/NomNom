from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.fields.html5 import EmailField, URLField
from wtforms.validators import InputRequired, Length, Optional, URL, Email
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_USER_IMG = os.getenv('DEFAULT_USER_IMG')
DEFAULT_RECIPE_IMG = os.getenv('DEFAULT_RECIPE_IMG')

class RegisterForm(FlaskForm):
    """Form for user sign up"""

    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('New Password', validators=[InputRequired(), Length(min=6)])
    

class LoginForm(FlaskForm):
    """Form for user login"""

    email = EmailField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    

class RecipeForm(FlaskForm):
    """Form for adding a recipe"""

    title = StringField('Title (Required)', validators=[InputRequired()])
    source_url = URLField('Source URL', validators=[Optional(), URL()])
    ingredients = TextAreaField('Ingredients', validators=[Optional()])
    instructions = TextAreaField('Intructions/Notes', validators=[Optional()])
    image_url = URLField('Image URL', validators=[Optional(), URL()], default=DEFAULT_RECIPE_IMG)
