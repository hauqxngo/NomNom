from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional, URL

DEFAULT_RECIPE_IMG = 'https://www.freeiconspng.com/uploads/free-recipe-sheet-clip-art-21.png'

class RegisterForm(FlaskForm):
    """Form for user sign up"""

    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired()])
    password = PasswordField('New Password', validators=[InputRequired(), Length(min=6)])


class LoginForm(FlaskForm):
    """Form for user login"""

    email = StringField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    

class RecipeForm(FlaskForm):
    """Form for adding a recipe"""

    title = StringField('Title', validators=[InputRequired()])
    source_url = StringField('Source URL', validators=[Optional(), URL()])
    ingredients = TextAreaField('Ingredients', validators=[Optional()])
    instructions = TextAreaField('Intructions', validators=[Optional()])
    image_url = StringField('Image URL', validators=[Optional()], default=DEFAULT_RECIPE_IMG)


class EditRecipeForm(FlaskForm):
    """Form for editing an existing recipe"""

    title = StringField('Title:', validators=[InputRequired()])
    source_url = StringField('Source URL:', validators=[Optional(), URL()])
    ingredients = TextAreaField('Ingredients:', validators=[Optional()])
    instructions = TextAreaField('Intructions:', validators=[Optional()])
    image_url = StringField('Image URL:', validators=[Optional(), URL()])
    leftovers = BooleanField('Leftovers?')




