"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest tests/test_user_views.py


from unittest import TestCase
from app import app, CURR_USER_KEY

from models import db, User

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///nomnom_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

db.create_all()

# Don't have WTForms use CSRF to test
app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.register(first_name='Test',
                                      last_name='User',
                                      email='test@test.com',
                                      pwd='testuser')
        self.testuser_id = 1111
        self.testuser.id = self.testuser_id

        self.u1 = User.register('Test1', 'User1', 'test1@test.com', 'password')
        self.u1_id = 111
        self.u1.id = self.u1_id

        db.session.add(self.testuser)
        db.session.commit()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_show(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            res = c.get(f'/users/{self.testuser_id}')

            self.assertEqual(res.status_code, 200)
            self.assertIn('Test User', str(res.data))

    def test_unauthorized_recipe_page_access(self):
        with self.client as c:

            res = c.get(f'/users/{self.testuser_id}/recipes', follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertNotIn('Test1', str(res.data))
            self.assertIn('Please log in first.', str(res.data))
