from flask import Flask, render_template, request, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Recipe, RecipeCuisine, Cuisine
from forms import RegisterForm, LoginForm
import requests
from key import API_SECRET_KEY

API_BASE_URL = "https://api.spoonacular.com"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///nomnom'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = 'ihaveasecret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/recipes')
def show_recipes():
    return render_template('recipes.html')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Show register form and handle user registration."""

    form = RegisterForm()

    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data
        
        new_user = User.register(first_name, last_name, email, password)

        db.session.add(new_user)
        db.session.commit()
        
        # should add some handling errors here
        flash('Welcome! Successfully created your account.')
        return redirect('/recipes')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # authenticate will return a user or False
        user = User.authenticate(email, password)

        if user:
            session["user_id"] = user.id  # keep logged in
            return redirect("/recipes")

        else:
            form.email.errors = ["Incorrect email or password. Please try again."]

    return render_template('login.html', form=form)