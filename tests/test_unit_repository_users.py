import datetime
import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactBase, ContactUpdate, ContactResponse
from src.repository.users import (
    get_user_by_email,
    bun_user_by_id,
    unbun_user_by_id,
    get_user_by_bunned_field,
    create_user,
    update_token,
    confirmed_email,
    update_avatar,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)


    async def test_get_user_by_email(self):
        user = User()
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(email="andrii@gmail.com", db=self.session)
        self.assertEqual(result, user)
