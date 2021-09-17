"""User model tests."""

# run these tests like:
#
#    python -m unittest tests/test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Recipe

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///nomnom-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.register('John', 'Doe', 'email1@email.com', 'password', None)
        uid1 = 1111
        u1.id = uid1

        u2 = User.register('Jane', 'Doe', 'email2@email.com', 'password', None)
        uid2 = 2222
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            first_name='Test',
            last_name='User',
            email='test@test.com',
            password='HASHED_PASSWORD',
        )

        db.session.add(u)
        db.session.commit()

        # User should have no recipes
        self.assertEqual(len(u.recipes), 0)


    ####
    # Signup Tests

    def test_valid_register(self):
        u_test = User.register('Test', 'User', 'testtest@test.com', 'password', None)
        uid = 3333
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.first_name, 'Test')
        self.assertEqual(u_test.last_name, 'User')
        self.assertEqual(u_test.email, 'testtest@test.com')
        self.assertNotEqual(u_test.password, 'password')
        # Bcrypt strings should start with $2b$
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_fname_register(self):
        invalid = User.register(None, 'Smith', 'test@test.com', 'password', None)
        uid = 4444
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_lname_register(self):
        invalid = User.register('Sam', None, 'test@test.com', 'password', None)
        uid = 5555
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_register(self):
        invalid = User.register('No', 'One', None, 'password', None)
        uid = 6666
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_password_register(self):
        with self.assertRaises(ValueError) as context:
            User.register('No', 'One', 'email@email.com', '', None)
        
        with self.assertRaises(ValueError) as context:
            User.register('No', 'One', 'email@email.com', None, None)
    
    ####
    # Authentication Tests

    def test_valid_authentication(self):
        u = User.authenticate(self.u1.email, 'password')
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)
    
    def test_invalid_email(self):
        self.assertFalse(User.authenticate('bademail', 'password'))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.u1.email, 'badpassword'))
