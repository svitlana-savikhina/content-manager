import unittest
from datetime import date, datetime
from unittest.mock import MagicMock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi import HTTPException

from database import Base
from posts import models, schemas
from posts.crud import (
    create_post,
    get_post_by_id,
    get_all_posts,
    update_post_by_id,
    delete_post_by_id,
    create_comment,
    get_comments_for_post,
    update_comment,
    delete_comment_by_id_and_post_id,
    get_comments_data,
)
from posts.models import Comment


class TestPostFunctions(unittest.TestCase):
    engine = None

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(cls.engine)

    def setUp(self):
        self.mock_db_session = MagicMock(spec=Session)
        self.db = self.Session()

    def tearDown(self):
        self.db.close()

    def test_create_post(self):
        # Test creating a post with valid data
        post_data = schemas.PostCreate(
            title="Test Post",
            content="This is a test post content.",
        )
        user_id = 1

        check_profanity = MagicMock(return_value=(False, ""))

        with patch("posts.crud.check_profanity", check_profanity):
            created_post = create_post(self.mock_db_session, post_data, user_id)

        self.assertEqual(created_post.title, post_data.title)
        self.assertEqual(created_post.content, post_data.content)
        self.assertEqual(created_post.user_id, user_id)

    def test_create_post_with_profane_content(self):
        # Test creating a post with profane content which should raise an HTTPException.
        post_data = schemas.PostCreate(
            title="Profane Title",
            content="This content contains profanity.",
        )
        user_id = 1

        check_profanity = MagicMock(return_value=(True, "Content is profane"))

        with patch("posts.crud.check_profanity", check_profanity):
            with self.assertRaises(HTTPException) as cm:
                create_post(self.mock_db_session, post_data, user_id)

        self.assertEqual(cm.exception.status_code, 400)

    def test_get_post_by_id(self):
        # Test retrieving a post by its ID
        post_id = 1
        mock_post = models.Post(
            id=post_id, title="Test Post", content="Test content", user_id=1
        )
        self.mock_db_session.query().filter().first.return_value = mock_post

        retrieved_post = get_post_by_id(self.mock_db_session, post_id)

        self.assertEqual(retrieved_post.id, post_id)
        self.assertEqual(retrieved_post.title, mock_post.title)

    def test_get_all_posts(self):
        # Test retrieving all posts
        mock_posts = [
            models.Post(id=1, title="Post 1", content="Content 1", user_id=1),
            models.Post(id=2, title="Post 2", content="Content 2", user_id=2),
        ]
        self.mock_db_session.query().offset().limit().all.return_value = mock_posts

        all_posts = get_all_posts(self.mock_db_session)

        self.assertEqual(len(all_posts), len(mock_posts))

    def test_update_post_by_id(self):
        # Test updating a post by its ID with valid data
        post_id = 1
        user_id = 1
        post_data = schemas.PostUpdate(title="Updated Title", content="Updated content")

        mock_post = models.Post(
            id=post_id, title="Test Post", content="Test content", user_id=user_id
        )
        self.mock_db_session.query().filter().first.return_value = mock_post

        check_profanity = MagicMock(return_value=(False, ""))

        with patch("posts.crud.check_profanity", check_profanity):
            updated_post = update_post_by_id(
                self.mock_db_session, post_id, post_data, user_id
            )

        self.assertEqual(updated_post.id, post_id)
        self.assertEqual(updated_post.title, post_data.title)
        self.assertEqual(updated_post.content, post_data.content)

    def test_delete_post_by_id(self):
        # Test deleting a post by its ID
        post_id = 1
        mock_post = models.Post(
            id=post_id, title="Test Post", content="Test content", user_id=1
        )
        self.mock_db_session.query().filter().first.return_value = mock_post

        result = delete_post_by_id(self.mock_db_session, post_id)

        self.assertTrue(result)

    def test_create_comment(self):
        # Test creating a comment with valid data
        comment_data = schemas.CommentCreate(
            content="This is a test comment.",
            created_at=datetime.now(),
            user_id=1,
            post_id=1,
        )
        user_id = 1
        post_id = 1

        check_profanity = MagicMock(return_value=(False, ""))

        with patch("posts.crud.check_profanity", check_profanity):
            created_comment = create_comment(
                self.mock_db_session, comment_data, user_id, post_id
            )

        self.assertEqual(created_comment.content, comment_data.content)
        self.assertEqual(created_comment.user_id, user_id)
        self.assertEqual(created_comment.post_id, post_id)

    def test_create_comment_with_profane_content(self):
        # Test creating a comment with profane content which should raise an HTTPException
        comment_data = schemas.CommentCreate(
            content="This content contains profanity.",
            created_at=datetime.now(),
            user_id=1,
            post_id=1,
        )

        check_profanity = MagicMock(return_value=(True, "Content is profane"))

        with patch("posts.crud.check_profanity", check_profanity):
            with self.assertRaises(HTTPException) as cm:
                create_comment(
                    self.mock_db_session,
                    comment_data,
                    comment_data.user_id,
                    comment_data.post_id,
                )

        self.assertEqual(cm.exception.status_code, 500)

    def test_get_comments_for_post(self):
        # Test retrieving comments for a specific post
        post_id = 1
        mock_comments = [
            models.Comment(
                id=1, content="Comment 1", user_id=1, post_id=post_id, blocked=False
            ),
            models.Comment(
                id=2, content="Comment 2", user_id=2, post_id=post_id, blocked=False
            ),
        ]
        self.mock_db_session.query().filter().offset().limit().all.return_value = (
            mock_comments
        )

        comments_for_post = get_comments_for_post(self.mock_db_session, post_id)

        self.assertEqual(len(comments_for_post), len(mock_comments))

    def test_update_comment(self):
        # Test updating a comment by its ID with valid data
        comment_id = 1
        comment_data = schemas.CommentUpdate(
            content="Updated comment content", updated_at=datetime.now()
        )

        mock_comment = models.Comment(
            id=comment_id, content="Test comment", user_id=1, post_id=1, blocked=False
        )
        self.mock_db_session.query().filter().first.return_value = mock_comment

        check_profanity = MagicMock(return_value=(False, ""))

        with patch("posts.crud.check_profanity", check_profanity):
            updated_comment = update_comment(
                self.mock_db_session, comment_id, comment_data
            )

        self.assertEqual(updated_comment.id, comment_id)
        self.assertEqual(updated_comment.content, comment_data.content)

    def test_delete_comment_by_id_and_post_id(self):
        # Test deleting a comment by its ID and post ID
        comment_id = 1
        post_id = 1
        mock_comment = models.Comment(
            id=comment_id,
            content="Test comment",
            user_id=1,
            post_id=post_id,
            blocked=False,
        )
        self.mock_db_session.query().filter().first.return_value = mock_comment

        result = delete_comment_by_id_and_post_id(
            self.mock_db_session, comment_id, post_id
        )

        self.assertTrue(result)

    def test_get_comments_data(self):
        # Test retrieving comment analytics data within a date range
        comments = [
            Comment(created_at=datetime(2023, 6, 25, 12, 0), blocked=False),
            Comment(created_at=datetime(2023, 6, 25, 13, 0), blocked=True),
            Comment(created_at=datetime(2023, 6, 26, 14, 0), blocked=False),
        ]
        self.db.add_all(comments)
        self.db.commit()

        date_from = date(2023, 6, 25)
        date_to = date(2023, 6, 26)

        result = get_comments_data(date_from, date_to, self.db)

        self.assertEqual(len(result), 2)

        first_day = result[0]
        self.assertEqual(first_day.date, date(2023, 6, 25))
        self.assertEqual(first_day.created_comments, 1)
        self.assertEqual(first_day.blocked_comments, 1)

        second_day = result[1]
        self.assertEqual(second_day.date, date(2023, 6, 26))
        self.assertEqual(second_day.created_comments, 1)
        self.assertEqual(second_day.blocked_comments, 0)


if __name__ == "__main__":
    unittest.main()
