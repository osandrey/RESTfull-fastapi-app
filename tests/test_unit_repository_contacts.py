import datetime
import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactBase, ContactUpdate, ContactResponse
from src.repository.contacts import (
    get_contacts,
    find_contacts,
    find_contacts_bday,
    get_contact,
    create_contact,
    remove_contact,
    update_contact,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_find_contact_found(self):
        contact = Contact()
        self.session.query().filter().filter().all.return_value = contact
        result = await find_contacts(user=self.user, db=self.session, firstname="Andrii")
        print(result)
        self.assertEqual(result, contact)

    async def test_create_contact(self):
        body = ContactBase(firstname="test", lastname="test-name", phone_number="test-phone-number", email="test-email",
                           description="test contact", date_of_birth=datetime.date(1990, 1, 1))

        user = User(id=1)
        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.firstname, body.firstname)
        self.assertEqual(result.lastname, body.lastname)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.description, body.description)
        self.assertEqual(result.date_of_birth, body.date_of_birth)
        self.assertEqual(result.user_id, user.id)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)



    async def test_update_contact_found(self):
        body_update = ContactUpdate(firstname="b-test",
                             lastname="test-name",
                             phone_number="test-phone-number",
                             email="test-email",
                             description="test contact",
                             date_of_birth=datetime.date(1990, 1, 1))
        user = User(id=1)
        print(f'USER:{user.id}')
        body = ContactBase(firstname="a-test",
            lastname="a-test-name",
            phone_number="a-test-phone-number",
            email="a-test-email",
            description="a-test contact",
            date_of_birth=datetime.date(1889, 2, 1))

        contact = await create_contact(body, user=user, db=self.session)
        print(f"CONTACT:{contact.firstname}")
        self.session.query().filter().first.return_value = contact
        self.session.query().filter().all.return_value = user
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body_update, user=user, db=self.session)
        print(f"RESULT:{result.user_id}")
        self.assertEqual(result.firstname, contact.firstname)
        self.assertEqual(result.user_id, contact.user_id)

    async def test_update_contact_not_found(self):
        body = ContactUpdate(firstname="test", lastname="test-name",
                             phone_number="test-phone-number",
                             email="test-email",
                             description="test contact",
                             date_of_birth=datetime.date(1990, 1, 1))
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_get_contact_bd_found(self):
        contact = Contact(firstname="test",
                          lastname="test-name",
                          phone_number="test-phone-number",
                          email="test-email",
                          description="test contact",
                          date_of_birth=datetime.date(1990, 7, 13))
        # self.session.query.return_value.filter.return_value.first.return_value = contact
        self.session.query().filter().all.return_value = [contact]
        result = await find_contacts_bday(days=7, user=self.user, db=self.session)
        self.assertEqual(result, [contact])
        self.assertEqual(result[0].firstname, contact.firstname)


if __name__ == '__main__':
    unittest.main()
