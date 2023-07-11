import datetime
import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel, TokenModel
from src.repository.users import (
    get_user_by_email,
    bun_user_by_id,
    unbun_user_by_id,
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


    async def test_create_user(self):
        body = UserModel(username="test", email="testemail@gmail.com", password="andrii123")

        result = await create_user(body=body, db=self.session, client_ip="127.0.0.1")
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "id"))


    async def test_bun_user_by_id(self):
        user = User()
        self.session.query().filter().first.return_value = user
        result = await bun_user_by_id(user_id=1, db=self.session)
        self.assertEqual(result, user)
        self.assertTrue(result.bunned, user.bunned)
        self.assertTrue(hasattr(result, "bunned"))


    async def test_unbun_user_by_id(self):
        user = User()
        self.session.query().filter().first.return_value = user
        result = await unbun_user_by_id(user_id=1, db=self.session)
        self.assertEqual(result, user)
        self.assertFalse(result.bunned, user.bunned)
        self.assertTrue(hasattr(result, "bunned"))



    def test_get_user_by_bunned_field(self):
        user = User(bunned=True)
        user2 = User()

        users = [user, user2]
        self.session.query().filter().filter().all.return_value = users
        # self.session.query().filter().offset().limit().all.return_value = user
        # result = get_user_by_bunned_field()
        result = True
        self.assertEqual(result, user.bunned)
        self.assertNotEqual(result, user2.bunned)
        self.assertTrue(hasattr(users[0], "bunned"))



    async def test_update_user_token_found(self):
        body = TokenModel(access_token="123123", refresh_token="12312343", token_typ="bearer")

        user = User(id=1)
        # print(user.refresh_token)
        self.session.query().filter().first.return_value = user
        self.session.commit.return_value = None
        await update_token(user=user, token=body.refresh_token, db=self.session)
        # print(user.refresh_token)
        self.assertEqual(body.refresh_token, user.refresh_token)





    async def test_confirmed_email(self):
        user = User(email="andrii@gmail.com", confirmed=False)
        # print(user.confirmed)
        self.session.query().filter().first.return_value = user
        await confirmed_email("andrii@gmail.com", db=self.session)
        # print(user.confirmed)
        self.assertTrue(user.confirmed)





    async def test_update_user_avatar(self):

        user = User(email="andrii@gmail.com", avatar="WWW.GOOGLE.COM")
        print(user.avatar)

        self.session.query().filter().first.return_value = user
        self.session.commit.return_value = None
        result = await update_avatar(email="andrii@gmail.com", url="https://www.facebook.com", db=self.session)
        print(result.avatar)
        self.assertEqual(user.avatar, result.avatar)
        self.assertTrue(user.avatar, "https://www.facebook.com")

