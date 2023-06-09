"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes

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

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)

        self.testuser3 = User.signup(username="testuser3",
                                    email="test3@test.com",
                                    password="testuser3",
                                    image_url=None)

        self.testuser.id = 1
        self.testuser2.id = 2
        self.testuser3.id = 3

        message1 = Message(id=1, text="test_message_views_text_1")
        message2 = Message(id=2, text="test_message_views_text_2")

        self.testuser.messages.append(message1)
        self.testuser.messages.append(message2)

        followed = self.testuser2
        follower = self.testuser3

        follower.following.append(followed)

        db.session.commit()

        like = Likes(
            user_id = self.testuser2.id,
            message_id = message1.id
        )

        db.session.add(like)

        db.session.commit()

        self.message1 = message1
        self.message2 = message2

        # Why is it making me do this? - Detached instance error if not. - Does not occur in other files.
        self.message1.id
        self.testuser.id
        self.testuser2.id
        self.testuser3.id
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

            resp = c.post("/signup", data={"username" : "testuser4", "email" : "test4@test.com", "password" : "testuser4", "image_url" : "testuser4.jpeg"})

            self.assertEqual(resp.status_code, 302)
            html = resp.get_data(as_text=True)
            self.assertIn('<a href="/">/</a>', html)

    def test_user_signup_post_redirect(self):
        """Is a user appropriately redirected if successful signup"""

        with self.client as c:

            resp = c.post("/signup", data={"username" : "testuser4", "email" : "test4@test.com", "password" : "testuser4", "image_url" : "testuser4.jpeg"}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('testuser4', html)
            self.assertIn('testuser4.jpeg', html)

    def test_user_signup_post_duplicate_username_redirect(self):
        """Is a user appropriately redirected if using duplicate username"""

        with self.client as c:

            resp = c.post("/signup", data={"username" : "testuser", "email" : "test4@test.com", "password" : "testuser4", "image_url" : "testuser4.jpeg"}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Username or email already taken', html)

    def test_user_signup_post_duplicate_email_redirect(self):
        """Is a user appropriately redirected if using duplicate email"""

        with self.client as c:

            resp = c.post("/signup", data={"username" : "testuser4", "email" : "test@test.com", "password" : "testuser4", "image_url" : "testuser4.jpeg"}, follow_redirects=True)

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

    def test_logout(self):
        """Can a user log out?"""

        with self.client as c:

            resp = c.post("/logout", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Goodbye!', html)

    def test_users_show_logged_in(self):
        """Can a logged in user see a page with other users?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/users")

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn('@testuser', html)

    def test_users_show_logged_out(self):
        """Can a logged out user see a page with other users?"""

        with self.client as c:

            resp = c.get("/users")

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn('@testuser', html)

    def test_users_show_logged_in_search(self):
        """Can a logged in user search for a user that does exist?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/users", query_string={"q":"testuser"})

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn('@testuser', html)

    def test_users_show_logged_out_search(self):
        """Can a logged out user search for a user that does exist?"""

        with self.client as c:

            resp = c.get("/users", query_string={"q":"testuser"})

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn('@testuser', html)

    def test_users_show_logged_in_search_no_value(self):
        """Can a logged in user search for a user that does not exist?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/users", query_string={"q":"not_existing_user"})

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertNotIn('@testuser', html)
            self.assertNotIn('@not_existing_user', html)

    def test_users_show_logged_out_search_no_value(self):
        """Can a logged out user search for a user that does not exist?"""

        with self.client as c:

            resp = c.get("/users", query_string={"q":"not_existing_user"})

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertNotIn('@testuser', html)
            self.assertNotIn('@not_existing_user', html)

    def test_show_specific_user_logged_in(self):
        """Can a user view a specific other user if logged in?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser2.id}")

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("@testuser2", html)

    def test_show_specific_user_logged_out(self):
        """Can a user view a specific other user if logged out?"""

        with self.client as c:

            resp = c.get(f"/users/{self.testuser2.id}")

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("@testuser2", html)


    def test_show_followers_logged_in(self):
        """Can a user view another user's followers if logged in?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser2.id}/followers")

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("@testuser3", html)

    def test_show_followers_logged_in_nobody_case(self):
        """Can a user view another user's followers if logged in? - If no followers"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser3.id}/followers")

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertNotIn("@testuser2", html)


    def test_show_following_logged_in(self):
        """Can a user view another user's following if logged in?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser3.id}/following")

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("@testuser2", html)

    def test_show_following_logged_in_nobody_case(self):
        """Can a user view another user's following if logged in? - If no followers"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser2.id}/following")

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertNotIn("@testuser3", html)

    def test_show_likes_logged_in(self):
        """Can a user view anotehr user's liked messages?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser3.id

            resp = c.get(f"/users/{self.testuser2.id}/likes")

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("test_message_views_text_1", html)

    def test_show_likes_logged_in_none_case(self):
        """Can a user view another user's empty liked messages page?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser3.id

            resp = c.get(f"/users/{self.testuser.id}/likes")

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertNotIn("test_message_views_text_1", html)
            self.assertIn('<ul class="list-group" id="messages">\n\n      \n\n    </ul>', html)


    def test_follow_logged_in(self):
        """Can a user follow another user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.post(f"/users/follow/{self.testuser2.id}", follow_redirects=True)

        self.assertEqual(resp.status_code, 200)

        html = resp.get_data(as_text=True)

        self.assertIn('@testuser2', html)
        self.assertNotIn('@testuser3', html)


    # def test_unfollow_logged_in(self):
    #     """Can a user follow another user?"""

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser3.id

    #     resp = c.post(f"/users/stop-following/{self.testuser2.id}", follow_redirects=True)

    #     self.assertEqual(resp.status_code, 200)

    #     html = resp.get_data(as_text=True)

    #     self.assertNotIn('@testuser2', html)


    def test_unfollow_logged_in(self):
        """Can a user follow another user?"""

        followed = self.testuser2
        follower = self.testuser

        follower.following.append(followed)

        db.session.commit()

        followed = self.testuser3
        follower = self.testuser

        follower.following.append(followed)

        db.session.commit()

        # Why is it making me do this? - Detached instance error if not. - Does not occur in other files.
        self.testuser2.id
        # Why is it making me do this? - Detached instance error if not. - Does not occur in other files.

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.post(f"/users/stop-following/{self.testuser2.id}", follow_redirects=True)

        self.assertEqual(resp.status_code, 200)

        html = resp.get_data(as_text=True)

        self.assertNotIn('@testuser2', html)
        self.assertIn('@testuser3', html)


    def test_edit_profile_get_logged_in(self):
        """Can a user get their profile edit form page?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.get(f"/users/profile")

        self.assertEqual(resp.status_code, 200)

        html = resp.get_data(as_text=True)

        self.assertIn("To confirm changes, enter your password:", html)
        self.assertIn("Enter your password to confirm", html)
        self.assertIn("Edit this user!", html)


    def test_edit_profile_post_logged_in(self):
        """Can a user edit their profile?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.post(f"/users/profile", data={"username" : "testuser_edited", "email" : "test@test.com", "password" : "testuser", "image_url" : "None"}, follow_redirects=True)

        self.assertEqual(resp.status_code, 200)

        html = resp.get_data(as_text=True)

        self.assertIn("testuser_edited", html)


    def test_delete_post_logged_in(self):
        """Can a user delete their account?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.post(f"/users/delete")

        self.assertEqual(resp.status_code, 302)

        check_all_users = User.query.order_by(User.id.asc()).all()

        self.assertNotEqual(check_all_users[0].username, "testuser")
        self.assertEqual(check_all_users[0].username, "testuser2")

