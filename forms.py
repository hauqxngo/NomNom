import datetime
from flask_wtf import FlaskForm
import datetime
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, DateField
from wtforms.fields.html5 import EmailField, URLField
from wtforms.validators import InputRequired, Length, Optional, URL, Email

DEFAULT_USER_IMG = 'https://www.freeiconspng.com/uploads/icon-user-blue-symbol-people-person-generic--public-domain--21.png'
DEFAULT_RECIPE_IMG = 'https://www.freeiconspng.com/uploads/free-recipe-sheet-clip-art-21.png'
DEFAULT_DATE = datetime.datetime.now()

class RegisterForm(FlaskForm):
    """Form for user sign up"""

    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('New Password', validators=[InputRequired(), Length(min=6)])
    image_url = URLField('Profile Picture URL (Optional)', validators=[Optional(), URL()], default=DEFAULT_USER_IMG)


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


class LeftoverForm(FlaskForm):
    """Form for editing an existing recipe"""

    leftovers = BooleanField('Leftovers?')
    done_on = DateField('I cooked this on:', default=DEFAULT_DATE)
