from flask import Flask, render_template, request
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Recipe, RecipeCuisine, Cuisine
from forms import UserForm
import requests
from key import API_SECRET_KEY

API_BASE_URL = "https://api.spoonacular.com"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///nomnom'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    return render_template('register.html')
