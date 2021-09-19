"""Models for Recipe app."""

import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


DEFAULT_USER_IMG = 'https://www.freeiconspng.com/uploads/icon-user-blue-symbol-people-person-generic--public-domain--21.png'
DEFAULT_RECIPE_IMG = 'https://www.freeiconspng.com/uploads/free-recipe-sheet-clip-art-21.png'


class User(db.Model):
    """Site user."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.Text, default=DEFAULT_USER_IMG)
    # email_confirmation_sent_on = db.Column(db.DateTime)
    # email_confirmed = db.Column(db.Boolean,default=False)
    # email_confirmed_on = db.Column(db.DateTime)

    recipes = db.relationship(
        'Recipe',
        backref='user',
        cascade='all, delete-orphan')

    @property
    def full_name(self):
        """Return full name of user."""

        return f'{self.first_name} {self.last_name}'

    @classmethod
    def register(cls, first_name, last_name, email, pwd, image_url):
        """Register user with hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode('utf8')

        # return instance of user with email & hashed pwd
        return cls(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_utf8,
            image_url=image_url
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
    source_url = db.Column(db.Text)
    ingredients = db.Column(db.Text)
    instructions = db.Column(db.Text)
    image_url = db.Column(db.Text, default=DEFAULT_RECIPE_IMG)
    created_on = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.now
    )
    done = db.Column(db.Boolean, default=False)
    leftovers = db.Column(db.Boolean, default=False)
    done_on = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # @property
    # def friendly_date(self):
    #     """Return nicely-formatted date."""

    #     return self.created_on.strftime('%Y, %m, %d')
