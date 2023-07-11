from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Contact, User
from src.schemas import ContactBase, ContactResponse, ContactUpdate
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=["Contacts"])


@router.get(
    "/", response_model=List[ContactResponse],
    description='No more than 5 requests per minute',
    dependencies=[Depends(RateLimiter(times=20, seconds=60))])
async def read_contacts(skip: int = 0, limit: int = 100, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The read_contacts function returns a list of contacts.

    :param skip: int: Skip the first n contacts
    :param limit: int: Limit the number of contacts returned
    :param user: User: Get the current user
    :param db: Session: Pass in the database session
    :return: A list of contacts
    :doc-author: OSA
    """
    contacts = await repository_contacts.get_contacts(skip, limit, user, db)
    return contacts


@router.get("/find", response_model=List[ContactResponse])
async def find_contacts(
    firstname: str = Query(None),
    lastname: str = Query(None),
    email: str = Query(None),
    user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
) -> List[Contact]:
    """
    The find_contacts function is used to find contacts in the database.
    It takes a firstname, lastname and email as parameters.
    The user parameter is used to get the current user from the auth_service module.
    The db parameter is used to get a connection with the database from our dependency function.
    :param firstname: str: Filter the contacts by firstname
    :param lastname: str: Filter the contacts by lastname
    :param email: str: Search for a contact by email
    :param user: User: Get the user from the token
    :param db: Session: Get a database session
    :param : Get the current user from the database
    :return: A list of contacts, so we need to define a contact schema
    :doc-author: OSA
    """
    contacts = await repository_contacts.find_contacts(db, user, firstname, lastname, email)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contacts


@router.get("/bday_soon", response_model=List[ContactResponse])
async def find_bday_contacts(days: int, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):

    """
    The find_bday_contacts function returns a list of contacts whose birthday is within the next X days.
    The function takes in an integer value for the number of days and returns a list of contact objects.
    :param days: int: Specify the number of days in which a contact's birthday falls
    :param user: User: Get the current user
    :param db: Session: Get the database session from the dependency
    :return: A list of contacts that have their birthday in the next 'days' days
    :doc-author: OSA
    """
    contacts = await repository_contacts.find_contacts_bday(days,user, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The read_contact function is used to retrieve a single contact from the database.
    It takes in an integer representing the ID of the contact, and returns a Contact object.
    :param contact_id: int: Specify the contact id to retrieve
    :param user: User: Get the current user from the auth_service
    :param db: Session: Pass the database session to the function
    :return: A contact object
    :doc-author: OSA
    """
    contact = await repository_contacts.get_contact(contact_id, user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, description='No more than 2 requests per minute', dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def create_contact(body: ContactBase, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The create_contact function creates a new contact in the database.
    The function takes a ContactBase object as input, which is validated by pydantic.
    The user who created the contact is also passed to the function and stored in the database.
    :param body: ContactBase: Get the body of the request
    :param user: User: Get the user from the auth_service
    :param db: Session: Access the database
    :return: A contactbase object, which is the same as the input body
    :doc-author: OSA
    """
    return await repository_contacts.create_contact(body, user, db)


@router.put("/{contact_id}", response_model=ContactResponse, description='No more than 2 requests per minute', dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def update_contact(body: ContactUpdate, contact_id: int, user: User = Depends(auth_service.get_current_user),db: Session = Depends(get_db)):
    """
    The update_contact function updates a contact in the database.
    The function takes an id, and a body containing the updated information for that contact.
    It then uses the update_contact method from repository_contacts to update that contact in the database.
    :param body: ContactUpdate: Pass the contact details to be updated
    :param contact_id: int: Identify the contact that will be deleted
    :param user: User: Get the current user from the auth_service
    :param db: Session: Pass the database session to the repository
    :return: A contact update object
    :doc-author: OSA
    """
    contact = await repository_contacts.update_contact(contact_id,user, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(contact_id: int, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The remove_contact function removes a contact from the database.
    :param contact_id: int: Specify the id of the contact to be removed
    :param user: User: Get the user object from the auth_service
    :param db: Session: Pass the database session to the repository layer
    :return: A contact object, which is the contact that was removed
    :doc-author: OSA
    """
    contact = await repository_contacts.remove_contact(contact_id, user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
