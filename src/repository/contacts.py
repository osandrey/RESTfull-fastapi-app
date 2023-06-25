from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from sqlalchemy import and_
from src.database.db import get_db
from src.database.models import Contact, User
from src.schemas import ContactBase, ContactUpdate


async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    return db.query(Contact).filter(Contact.user_id==user.id).offset(skip).limit(limit).all()




async def find_contacts_bday(days, user: User, db: Session) -> List[Contact]:
    date_now = datetime.now().date()
    delta = days
    end_date = date_now + timedelta(days=delta)
    bdays_list = []
    all_contacts = db.query(Contact).filter(Contact.user_id==user.id).all()
    for contact in all_contacts:
        contact_bday_this_year = contact.date_of_birth.replace(year=date_now.year)
        # print(date_now, contact_bday_this_year, end_date, sep='\n')
        if date_now <= contact_bday_this_year <= end_date:
            bdays_list.append(contact)
    return bdays_list


async def find_contacts(
        db: Session,
        user: User,
        firstname: str = None,
        lastname: str = None,
        email: str = None,

) -> List[Contact]:
    query = db.query(Contact).filter(Contact.user_id==user.id)

    if firstname:
        query = query.filter(Contact.firstname.ilike(f"%{firstname}%"))
    if lastname:
        query = query.filter(Contact.lastname.ilike(f"%{lastname}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))

    contact = query.all()
    return contact


async def get_contact(contact_id: int,user: User, db: Session) -> Contact:
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactBase, user: User, db: Session) -> Contact:
    contact = Contact(
        firstname=body.firstname,
        lastname=body.lastname,
        email=body.email,
        phone_number=body.phone_number,
        date_of_birth=body.date_of_birth,
        description=body.description,
        user_id=user.id
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id==user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(contact_id: int, user: User, body: ContactUpdate, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id==user.id)).first()
    if contact:
        contact.firstname = body.firstname
        contact.lastname = body.lastname
        contact.phone_number = body.phone_number
        contact.email = body.email
        contact.date_of_birth = body.date_of_birth
        contact.description = body.description

        db.commit()
    return contact
