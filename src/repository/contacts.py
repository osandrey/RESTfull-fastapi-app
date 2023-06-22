from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Contact
from src.schemas import ContactBase, ContactUpdate


async def get_contacts(skip: int, limit: int, db: Session) -> List[Contact]:
    return db.query(Contact).offset(skip).limit(limit).all()



# async def get_contact(
#     contact_id: int,
#     db: Session = Depends(get_db),
#     firstname: str = None,
#     lastname: str = None,
#     email: str = None,
#
# ) -> List[Contact]:
#     query = db.query(Contact)
#
#     if firstname:
#         query = query.filter(Contact.firstname.ilike(f"%{firstname}%"))
#     if lastname:
#         query = query.filter(Contact.lastname.ilike(f"%{lastname}%"))
#     if email:
#         query = query.filter(Contact.email.ilike(f"%{email}%"))
#
#     contact = query.all()
#     return contact



async def get_contact(contact_id: int, db: Session) -> Contact:
    return db.query(Contact).filter(Contact.id == contact_id).first()


async def create_contact(body: ContactBase, db: Session) -> Contact:
    contact = Contact(
        firstname=body.firstname,
        lastname=body.lastname,
        email=body.email,
        phone_number=body.phone_number,
        date_of_birth=body.date_of_birth,
        description=body.description,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(contact_id: int, body: ContactUpdate, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        contact.firstname = body.firstname
        contact.lastname = body.lastname
        contact.phone_number = body.phone_number
        contact.email = body.email
        contact.date_of_birth = body.date_of_birth
        contact.description = body.description

        db.commit()
    return contact
