"""Message model tests."""

import os
import datetime
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

db.create_all()

class MessageModelTestCase(TestCase):
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

        message1 = Message(text="test_message_model_text")
        message2 = Message(text="test_message_model_text_2")

        user1.messages.append(message1)
        user1.messages.append(message2)

        db.session.commit()

        self.user1 = user1
        self.user2 = user2
        self.message1 = message1
        self.message2 = message2


    def tearDown(self):
        """Clean up any fouled transaction. Remove data from database after test completed."""
        db.session.rollback()

    def test_message_model(self):
        """Create a message and add to a user"""

        self.assertIsNotNone(len(self.user1.messages))
        self.assertEqual(self.message1.id, self.message2.id - 1)
        self.assertEqual(self.message1.text, "test_message_model_text")
        self.assertIsNotNone(self.message1.timestamp)
        self.assertEqual(f"{self.message1.timestamp}"[0:10], f"{datetime.datetime.utcnow()}"[0:10])
        self.assertEqual(self.message1.user_id, self.user1.id)

    # def tests_message_show_user()


    # def test_message_delete_cascade()