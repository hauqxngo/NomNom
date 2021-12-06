"""Recipe View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest tests/test_recipe_views.py


from unittest import TestCase
from app import app, CURR_USER_KEY

from models import db, User, Recipe

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///nomnom_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

db.create_all()

# Don't have WTForms use CSRF to test
app.config['WTF_CSRF_ENABLED'] = False


class RecipeViewTestCase(TestCase):
    """Test views for recipes."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.register(first_name='Test',
                                      last_name='User',
                                      email='test@test.com',
                                      pwd='testuser')
                
        self.testuser_id = 9999
        self.testuser.id = self.testuser_id

        db.session.add(self.testuser)
        db.session.commit()

    def test_add_recipe(self):
        """Test to add a new recipe."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            res = c.post('/recipes/new')

            r = Recipe(
                title='EZ Pizza',
                source_url='',
                ingredients='',
                instructions='',
                image_url='',
                user_id=self.testuser_id
            )

            # Make sure it redirects
            self.assertEqual(res.status_code, 200)

            db.session.commit()
            self.assertEqual(r.title, 'EZ Pizza')

    def test_add_no_session(self):
        with self.client as c:
            resp = c.post('/recipes/new', data={'title': 'EZ Pizza'}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in first.', str(resp.data))

    def test_add_invalid_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 7749 # user does not exist

            res = c.post('/recipes/new', data={'title': 'EZ Pizza'}, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('Please log in first.', str(res.data))
    
    def test_recipe_show(self):

        r = Recipe(
            id=1234,
            title="a new recipe",
            source_url='',
            ingredients='',
            instructions='',
            image_url='',        
            user_id=self.testuser_id
        )
        
        db.session.add(r)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            r = Recipe.query.get(1234)

            res = c.get(f'/recipes/{r.id}')

            self.assertEqual(res.status_code, 200)
            self.assertIn(r.title, str(res.data))

    def test_invalid_recipe_show(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get('/recipes/968673')

            self.assertEqual(resp.status_code, 404)

    def test_recipe_delete(self):

        r = Recipe(
            id=1234,
            title="a test recipe",
            user_id=self.testuser_id
        )
        db.session.add(r)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = c.post('/recipes/1234/delete', follow_redirects=True)
            self.assertEqual(res.status_code, 200)

            r = Recipe.query.get(1234)
            self.assertIsNone(r)

    def test_unauthorized_recipe_delete(self):

        # A second user that will try to delete the message
        u = User.register(first_name="unauthorized",
                        last_name='hacker',
                        email='testtest@test.com',
                        pwd='password')
        u.id = 3345

        # Recipe is owned by testuser
        r = Recipe(
            id=1234,
            title='a test recipe',
            user_id=self.testuser_id
        )
        db.session.add_all([u, r])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 3345

            res = c.post('/recipes/1234/delete', follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('Access unauthorized.', str(res.data))

            r = Recipe.query.get(1234)
            self.assertIsNotNone(r)

    def test_recipe_delete_no_authentication(self):

        r = Recipe(
            id=1234,
            title='a test recipe',
            user_id=self.testuser_id
        )
        db.session.add(r)
        db.session.commit()

        with self.client as c:
            res = c.post('/recipes/1234/delete', follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('Access unauthorized.', str(res.data))

            r = Recipe.query.get(1234)
            self.assertIsNotNone(r)
