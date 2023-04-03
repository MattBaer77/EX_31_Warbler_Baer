"""Message model tests."""

import os
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


    def tearDown(self):
        """Clean up any fouled transaction. Remove data from database after test completed."""
        db.session.rollback()

    def test_message_model(self):
        """Create a message and add to a user"""

        users = User.query.order_by(User.id.asc()).all()
        user1 = users[0]

        message = Message(text="test_message_model_text")

        user1.messages.append(message)

        db.session.commit()

        self.assertIsNotNone(len(user1.messages))
        self.assertEqual(message.user_id, user1.id)
        