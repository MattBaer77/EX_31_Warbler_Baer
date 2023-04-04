"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser.id = 1

        message1 = Message(id=1, text="test_message_views_text_1")
        message2 = Message(id=2, text="test_message_views_text_2")

        self.testuser.messages.append(message1)
        self.testuser.messages.append(message2)

        db.session.commit()

        self.message1 = message1
        self.message2 = message2

        # Why is it making me do this? - Detached instance error if not. - Does not occur in other files.
        self.message1.id
        # Why is it making me do this? - Detached instance error if not. - Does not occur in other files.

    def tearDown(self):
        """Clean up any fouled transaction."""
        
        db.session.rollback()

    def test_user_signup_get(self):
        """Can a user view sign up page"""

        with self.client as c:

            resp = c.get("/signup")

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<button class="btn btn-primary btn-lg btn-block">Sign me up!</button>', html)

    def test_user_signup_post(self):
        """Can a user sign up"""

        with self.client as c:

            resp = c.post("/signup", data={"username" : "testuser2", "email" : "test2@test.com", "password" : "testuser2", "image_url" : "testuser2.jpeg"})

            self.assertEqual(resp.status_code, 302)
            html = resp.get_data(as_text=True)
            self.assertIn('<a href="/">/</a>', html)

    def test_user_signup_post_redirect(self):
        """Is a user appropriately redirected if successful signup"""

        with self.client as c:

            resp = c.post("/signup", data={"username" : "testuser2", "email" : "test2@test.com", "password" : "testuser2", "image_url" : "testuser2.jpeg"}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('testuser2', html)
            self.assertIn('testuser2.jpeg', html)

    def test_user_signup_post_duplicate_username_redirect(self):
        """Is a user appropriately redirected if using duplicate username"""

        with self.client as c:

            resp = c.post("/signup", data={"username" : "testuser", "email" : "test2@test.com", "password" : "testuser2", "image_url" : "testuser2.jpeg"}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Username or email already taken', html)

    def test_user_signup_post_duplicate_email_redirect(self):
        """Is a user appropriately redirected if using duplicate email"""

        with self.client as c:

            resp = c.post("/signup", data={"username" : "testuser2", "email" : "test@test.com", "password" : "testuser2", "image_url" : "testuser2.jpeg"}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Username or email already taken', html)

    def test_login_get(self):
        """Can a user view login page"""

        with self.client as c:

            resp = c.get("/login")

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<button class="btn btn-primary btn-block btn-lg">Log in</button>', html)

    def test_login_get_already_logged_in(self):
        """User redirected away from login page if logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get("/login", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('You are already logged in!', html)

    def test_login_post(self):
        """Can a user log in"""

        with self.client as c:

            resp = c.post("/login", data={"username" : "testuser", "password" : "testuser"})

            self.assertEqual(resp.status_code, 302)
            html = resp.get_data(as_text=True)
            self.assertIn('<a href="/">/</a>', html)

    def test_login_post_redirect(self):
        """Can a user log in"""

        with self.client as c:

            resp = c.post("/login", data={"username" : "testuser", "password" : "testuser"}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<aside class="col-md-4 col-lg-3 col-sm-12" id="home-aside">', html)
            self.assertIn('<p>@testuser</p>', html)

    def test_login_wrong_username(self):
        """Is a user redirected and informed if username is incorrect"""

        with self.client as c:

            resp = c.post("/login", data={"username" : "incorrect_user_name", "password" : "testuser"}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Invalid credentials.', html)

    def test_login_wrong_password(self):
        """Is a user redirected and informed if password is incorrect"""

        with self.client as c:

            resp = c.post("/login", data={"username" : "testuser", "password" : "incorrect_password"}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Invalid credentials.', html)

    # def logout(self):
    #     """Is a user redirected and informed if password is incorrect"""

    #     with self.client as c:

    #         resp = c.post("/login", data={"username" : "testuser", "password" : "incorrect_password"}, follow_redirects=True)

    #         self.assertEqual(resp.status_code, 200)
    #         html = resp.get_data(as_text=True)
    #         self.assertIn('Invalid credentials.', html)
