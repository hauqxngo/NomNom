"""Models for Recipe app."""

import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
# db.create_all()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


DEFAULT_USER_IMG = 'https://www.freeiconspng.com/uploads/icon-user-blue-symbol-people-person-generic--public-domain--21.png'
DEFAULT_RECIPE_IMG = 'https://www.freeiconspng.com/uploads/recipe-icon-1.png'


class User(db.Model):
    """Site user."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    image_url = db.Column(db.Text, default=DEFAULT_USER_IMG)

    recipes = db.relationship(
        'Recipe',
        backref='user',
        cascade='all, delete-orphan')

    @property
    def full_name(self):
        """Return full name of user."""

        return f'{self.first_name} {self.last_name}'

    @classmethod
    def register(cls, first_name, last_name, email, pwd):
        """Register user with hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode('utf8')

        # return instance of user with email & hashed pwd
        return cls(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_utf8
            )

    @classmethod
    def authenticate(cls, email, pwd):
        """Validate that user exists & password is correct.
    
        Return user if valid; else return False.
        """

        u = User.query.filter_by(email=email).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False


class Recipe(db.Model):
    """Recipe input from user."""

    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.Text)
    directions = db.Column(db.Text)
    image_url = db.Column(db.Text, default=DEFAULT_RECIPE_IMG)
    created_on = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.now
    )
    leftovers = db.Column(db.Boolean, default=False)
    done = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'ingredients': self.ingredients,
            'directions': self.directions,
            'image_url': self.image_url,
            'created_on': self.created_on,
            'leftovers': self.leftovers,
            'done': self.done
        }

    # @property
    # def friendly_date(self):
    #     """Return nicely-formatted date."""

    #     return self.created_on.strftime('%a %b %d %Y')


class RecipeCuisine(db.Model):
    """Cuisine of a recipe."""

    __tablename__ = 'recipes_cuisines'

    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey('recipes.id'),
        primary_key=True)
    cuisine_id = db.Column(
        db.Integer,
        db.ForeignKey('cuisines.id'),
        primary_key=True)


class Cuisine(db.Model):
    """Cuisines that can be added to recipes."""

    __tablename__ = 'cuisines'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=True)

    recipes = db.relationship(
        'Recipe',
        secondary='recipes_cuisines',
        # cascade='all,delete',
        backref='cuisines'
    )
