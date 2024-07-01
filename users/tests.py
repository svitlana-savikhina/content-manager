import unittest
from unittest.mock import MagicMock

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from users import crud
from users.crud import ALGORITHM, SECRET_KEY
from users.schemas import UserCreate


class TestUserFunctions(unittest.TestCase):

    def setUp(self):
        # Set up mock database session or use a real one if available
        self.mock_db_session = MagicMock(spec=Session)

    def test_create_user(self):
        # Test user creation function
        user_create_data = UserCreate(username="testuser", password="testpassword")
        created_user = crud.create_user(self.mock_db_session, user_create_data)
        self.assertEqual(created_user.username, user_create_data.username)

    def test_create_access_token(self):
        # Test access token creation function
        data = {"sub": "testuser"}
        token = crud.create_access_token(data)
        self.assertIsInstance(token, str)

        decoded_data = crud.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        self.assertEqual(decoded_data["sub"], "testuser")

    def test_get_current_user(self):
        # Test current user retrieval function
        token = crud.create_access_token({"sub": "testuser"})
        with unittest.mock.patch("users.crud.decode", return_value={"sub": "testuser"}):
            authenticated_user = crud.get_current_user(
                db=self.mock_db_session, token=token
            )
            self.assertIsNotNone(authenticated_user)

        # Test invalid token scenario
        invalid_token = "invalidtoken"
        with self.assertRaises(HTTPException) as cm:
            crud.get_current_user(db=self.mock_db_session, token=invalid_token)
        self.assertEqual(cm.exception.status_code, status.HTTP_401_UNAUTHORIZED)
