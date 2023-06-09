"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


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


class MessageViewTestCase(TestCase):
    """Test views for messages."""

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

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of our tests

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            html = resp.get_data(as_text=True)

            message = Message.query.order_by(Message.id.asc()).all()
            message3 = message[2]

            self.assertEqual(message3.text, "Hello")
            self.assertEqual(message3.user.id, self.testuser.id)
            self.assertIn(f'<a href="/users/{self.testuser.id}">/users/{self.testuser.id}</a>', html)


    def test_add_message_follow_redirects(self):
        """Can user add a message? - Follow Redirects"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            message = Message.query.order_by(Message.id.asc()).all()
            message3 = message[2]

            self.assertEqual(message3.text, "Hello")
            self.assertEqual(message3.user.id, self.testuser.id)
            self.assertIn(f'Hello', html)


    def test_add_message_no_user(self):
        """Can user add a message if not logged in?"""

        with self.client as c:

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Access unauthorized.', html)


    def test_show_message(self):
        """Can user see a specific message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/messages/{self.message1.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            msg = Message.query.first()
            self.assertEqual(msg.text, "test_message_views_text_1")
            self.assertEqual(msg.user.id, self.testuser.id)
            self.assertIn("test_message_views_text_1", html)


    def test_show_message_no_user(self):
        """Can user see a specific message if not logged in?"""

        with self.client as c:

            resp = c.get(f"/messages/{self.message1.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            msg = Message.query.first()
            self.assertEqual(msg.text, "test_message_views_text_1")
            self.assertEqual(msg.user.id, self.testuser.id)
            self.assertIn("test_message_views_text_1", html)

    def test_delete_message(self):
        """Can user delete a their own message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/messages/{self.message1.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            msg = Message.query.first()
            self.assertEqual(msg.text, "test_message_views_text_2")
            self.assertNotIn("test_message_views_text_1", html)

    def test_unauthorized_delete_message_wrong_user(self):
        """Can user delete another users's message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 2

            resp = c.post(f"/messages/{self.message1.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)

    def test_unauthorized_delete_message_wrong_user(self):
        """Can user delete another users's message if not logged in?"""

        with self.client as c:

            resp = c.post(f"/messages/{self.message1.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)