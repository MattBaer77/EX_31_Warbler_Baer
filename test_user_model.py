"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


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

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        user1 = User(
            email="test1@test.com",
            username="test1user",
            password="HASHED_PASSWORD1"
        )

        user2 = User(
            email="test2@test.com",
            username="test2user",
            password="HASHED_PASSWORD2",
            image_url="image2.png",
            header_image_url="header_image2.png",
            bio="Some bio text for test 2",
            location="Some location for test 2",
        )

        db.session.add_all([user1, user2])
        db.session.commit()

        self.user1_testID = user1.id

    def tearDown(self):
        """Clean up any fouled transaction. Remove data from database after test completed."""

        db.session.rollback()

        # ASK ABOUT THIS APPROACH - Delete after to not leave anything in database?

        # User.query.delete()
        # Message.query.delete()
        # Follows.query.delete()

        # db.session.commit()

        # ASK ABOUT THIS APPROACH

    def test_user_model(self):
        """Set up a third user - Does basic model work? - Do all attributes and defaults work?"""

        user3 = User(
            email="test3@test.com",
            username="test3user",
            password="HASHED_PASSWORD3",
            image_url="image3.png",
            header_image_url="header_image3.png",
            bio="Some bio text for test 3",
            location="Some location for test 3"
        )

        db.session.add(user3)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(user3.messages), 0)
        self.assertEqual(len(user3.followers), 0)

        # "user3" should be the second user
        users = User.query.order_by(User.id.asc()).all()
        self.assertEqual(len(users), 3)

        # users[0].id should be 1 less than users[1].id
        self.assertEqual(users[0].id, (users[1].id - 1))

        # users[0].id should be 2 less than users[2].id
        self.assertEqual(users[0].id, (users[2].id - 2))

        # user3 attributes should equal those set above
        self.assertEqual(user3.email, "test3@test.com")
        self.assertEqual(user3.username, "test3user")
        self.assertEqual(user3.password, "HASHED_PASSWORD3")
        self.assertEqual(user3.image_url, "image3.png")
        self.assertEqual(user3.header_image_url, "header_image3.png")
        self.assertEqual(user3.bio, "Some bio text for test 3")
        self.assertEqual(user3.location, "Some location for test 3")

        # user[0] attributes should equal those set in setUp or the model defaults
        self.assertEqual(users[0].email, "test1@test.com")
        self.assertEqual(users[0].username, "test1user")
        self.assertEqual(users[0].password, "HASHED_PASSWORD1")
        self.assertEqual(users[0].image_url, "/static/images/default-pic.png")
        self.assertEqual(users[0].header_image_url, "/static/images/warbler-hero.jpg")
        self.assertEqual(users[0].bio, None)
        self.assertEqual(users[0].location, None)

    def test___repr__(self):
        """Test __repr__ functions"""

        users = User.query.order_by(User.id.asc()).all()
        user1 = users[0]
        user2 = users[1]

        self.assertEqual(user1.__repr__(),f"<User #{user1.id}: test1user, test1@test.com>")
        self.assertEqual(user2.__repr__(),f"<User #{user2.id}: test2user, test2@test.com>")

    def test_following(self):
        """Test is_following functions"""

        users = User.query.order_by(User.id.asc()).all()
        user1 = users[0]
        user2 = users[1]

        user2.following.append(user1)
        db.session.commit()

        self.assertEqual(len(user1.following), 0)
        self.assertEqual(len(user2.following), 1)
        self.assertEqual(user1.following, [])
        self.assertEqual(user2.following, [user1])

    def test_followers(self):
        """Test is_following functions"""

        users = User.query.order_by(User.id.asc()).all()
        user1 = users[0]
        user2 = users[1]

        user2.followers.append(user1)
        db.session.commit()

        self.assertEqual(len(user1.followers), 0)
        self.assertEqual(len(user2.followers), 1)
        self.assertEqual(user1.followers, [])
        self.assertEqual(user2.followers, [user1])

    def test_is_following(self):
        """Test is_following functions"""

        users = User.query.order_by(User.id.asc()).all()
        user1 = users[0]
        user2 = users[1]

        user2.following.append(user1)
        db.session.commit()

        self.assertEqual(user1.is_following(user2), False)
        self.assertEqual(user2.is_following(user1), True)

    def test_is_followed_by(self):
        """Test is_followed_by functions"""

        users = User.query.order_by(User.id.asc()).all()
        user1 = users[0]
        user2 = users[1]

        user2.followers.append(user1)
        db.session.commit()

        self.assertEqual(user1.is_followed_by(user2), False)
        self.assertEqual(user2.is_followed_by(user1), True)

    def test_signup_success(self):
        """Test signup classmethod"""

        user3 = User.signup("test3user", "test3@test.com", "Hash_this_pass", "image3.png")

        db.session.commit()

        # user3 attributes should equal those set above
        self.assertEqual(user3.email, "test3@test.com")
        self.assertEqual(user3.username, "test3user")
        self.assertEqual(user3.image_url, "image3.png")
        self.assertNotEqual(user3.password, "Hash_this_pass")
        self.assertTrue("$2b$" in user3.password)

    def test_signup_username_fail_duplicate(self):
        """Test signup classmethod"""

        with self.assertRaises(exc.IntegrityError) as context:
            user2 = User.signup("test2user", "test3@test.com", "Hash_this_pass", "image3.png")
            db.session.commit()

    def test_signup_email_fail_duplicate(self):
        """Test signup classmethod"""

        with self.assertRaises(exc.IntegrityError) as context:
            user2 = User.signup("test3user", "test2@test.com", "Hash_this_pass", "image3.png")
            db.session.commit()

    def test_signup_username_fail_None(self):
        """Test signup classmethod"""

        with self.assertRaises(exc.IntegrityError) as context:
            user2 = User.signup(None, "test3@test.com", "Hash_this_pass", "image3.png")
            db.session.commit()

    def test_signup_email_fail_None(self):
        """Test signup classmethod"""

        with self.assertRaises(exc.IntegrityError) as context:
            user2 = User.signup("test3user", None, "Hash_this_pass", "image3.png")
            db.session.commit()

    def test_signup_password_fail_None(self):
        """Test signup classmethod"""

        with self.assertRaises(ValueError) as context:
            user2 = User.signup("test3user", "test3@test.com", None, "image3.png")
            db.session.commit()

        with self.assertRaises(ValueError) as context:
            user2 = User.signup("test3user", "test3@test.com", "", "image3.png")
            db.session.commit()

    def test_authenticate_success(self):
        """Test authenticate classmethod"""

        user3 = User.signup("test3user", "test3@test.com", "Hash_this_pass", "image3.png")
        db.session.commit()

        userCheck = User.authenticate("test3user", "Hash_this_pass")

        self.assertIsNotNone(userCheck)
        self.assertEqual(userCheck.id, user3.id)
        self.assertEqual(userCheck.username, user3.username)
        self.assertEqual(userCheck.username, "test3user")

    def test_authenticate_fail_username(self):
        """Test authenticate classmethod"""

        user3 = User.signup("test3user", "test3@test.com", "Hash_this_pass", "image3.png")
        db.session.commit()

        userCheck = User.authenticate("Incorrect", "Hash_this_pass")

        self.assertFalse(userCheck)

    def test_authenticate_fail_password(self):
        """Test authenticate classmethod"""

        user3 = User.signup("test3user", "test3@test.com", "Hash_this_pass", "image3.png")
        db.session.commit()

        userCheck = User.authenticate("test3user", "Incorrect")

        self.assertFalse(userCheck)









