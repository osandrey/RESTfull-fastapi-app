from typing import List, Type

from fastapi import Depends
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from sqlalchemy import and_
from src.database.db import get_db
from src.database.models import Contact, User
from src.schemas import ContactBase, ContactUpdate


async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """
    The get_contacts function returns a list of contacts for the user.

    :param skip: int: Skip the first n contacts in the database
    :param limit: int: Limit the number of contacts returned
    :param user: User: Get the user_id from the database
    :param db: Session: Access the database
    :return: A list of contacts
    :doc-author: OSA
    """
    return db.query(Contact).filter(Contact.user_id==user.id).offset(skip).limit(limit).all()




async def find_contacts_bday(days, user: User, db: Session) -> List[Contact]:
    """
    The find_contacts_bday function takes in a number of days and returns all contacts whose birthdays fall within that range.
        Args:
            days (int): The number of days to look ahead for upcoming birthdays.
            user (User): The User object associated with the current session. This is used to filter out contacts belonging to other users.
            db (Session): A database Session object, which is used by SQLAlchemy's ORM methods for querying the database and retrieving results.

    :param days: Specify the number of days to look ahead for birthdays
    :param user: User: Get the user_id from the user object
    :param db: Session: Pass the database session to the function
    :return: A list of contacts whose birthday is within a given number of days
    :doc-author: OSA
    """
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
    """
    The find_contacts function is used to search for contacts in the database.
    It takes a user object, and optional firstname, lastname, and email parameters.
    The function returns a list of Contact objects that match the search criteria.

    :param db: Session: Pass the database session to the function
    :param user: User: Get the user id from the database
    :param firstname: str: Filter the results by firstname
    :param lastname: str: Filter the contacts by lastname
    :param email: str: Filter the contacts by email
    :param : Filter the contacts by firstname, lastname and email
    :return: A list of contacts, which is a list of dictionaries
    :doc-author: OSA
    """
    query = db.query(Contact).filter(Contact.user_id==user.id)

    if firstname:
        query = query.filter(Contact.firstname.ilike(f"%{firstname}%"))
    if lastname:
        query = query.filter(Contact.lastname.ilike(f"%{lastname}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))

    contact = query.all()
    return contact


async def get_contact(contact_id: int,user: User, db: Session) -> Type[Contact] | None:
    """
    The get_contact function returns a contact from the database.
        Args:
            contact_id (int): The id of the contact to be retrieved.
            user (User): The user who is requesting this information. This is used for authorization purposes, as only contacts belonging to that user can be accessed by them.
            db (Session): A connection to the database which will allow us to query it and retrieve data from it using SQLAlchemy's ORM methods and classes such as Contact, User, etc...

    :param contact_id: int: Specify the id of the contact to be retrieved
    :param user: User: Get the user from the database
    :param db: Session: Pass the database session to the function
    :return: The contact with the given id and user
    :doc-author: OSA
    """
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactBase, user: User, db: Session) -> Contact:
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactBase: Get the contact information from the request body
    :param user: User: Get the user_id from the logged in user
    :param db: Session: Access the database
    :return: The contact that was created
    :doc-author: OSA
    """
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
    """
    The remove_contact function removes a contact from the database.
        Args:
            contact_id (int): The id of the contact to be removed.
            user (User): The user who is removing the contact. This is used to ensure that only contacts belonging to this user are removed, and not other users' contacts by mistake or maliciously.
            db (Session): A session object for interacting with our database

    :param contact_id: int: Identify the contact to be removed
    :param user: User: Get the user_id from the user object
    :param db: Session: Pass the database session into the function
    :return: The contact that was removed
    :doc-author: OSA
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id==user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(contact_id: int, user: User, body: ContactUpdate, db: Session) -> Contact | None:
    """
    The update_contact function updates a contact in the database.
        Args:
            contact_id (int): The id of the contact to update.
            user (User): The user who is updating the contact. This is used for authorization purposes, as only contacts belonging to this user can be updated by them.
            body (ContactUpdate): A ContactUpdate object containing all of the information that will be updated on this particular Contact object in our database.

    :param contact_id: int: Identify the contact to be deleted
    :param user: User: Check if the user is authenticated and authorized to perform this action
    :param body: ContactUpdate: Pass the data from the request body to the function
    :param db: Session: Access the database
    :return: The updated contact
    :doc-author: OSA
    """
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
