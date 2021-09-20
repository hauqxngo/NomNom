"""Recipe Model tests."""

# run these tests like:
#
#    python -m unittest tests/test_recipe_model.py

from app import app, CURR_USER_KEY
from unittest import TestCase
from models import db, Recipe, User

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///nomnom_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

db.create_all()


class RecipeModelTestCase(TestCase):
    """Test recipe model."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.uid = 1111
        u = User.register('Test', 'User', 'testing@test.com', 'password', None)
        u.id = self.uid

        db.session.add(u)
        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_recipe_model(self):
        """Does basic model work?"""

        r = Recipe(
            title="New Recipe",
            source_url='',
            ingredients='',
            instructions='',
            image_url='',
            user_id=self.uid
        )

        db.session.add(r)
        db.session.commit()

        # User should have 1 recipe
        self.assertEqual(len(self.u.recipes), 1)
        self.assertEqual(self.u.recipes[0].title, "New Recipe")
