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
    dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def read_contacts(skip: int = 0, limit: int = 100, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
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
    contacts = await repository_contacts.find_contacts(db, user, firstname, lastname, email)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contacts


@router.get("/bday_soon", response_model=List[ContactResponse])
async def find_bday_contacts(days: int, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):

    contacts = await repository_contacts.find_contacts_bday(days,user, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    contact = await repository_contacts.get_contact(contact_id, user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, description='No more than 2 requests per minute', dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def create_contact(body: ContactBase, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    return await repository_contacts.create_contact(body, user, db)


@router.put("/{contact_id}", response_model=ContactResponse, description='No more than 2 requests per minute', dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def update_contact(body: ContactUpdate, contact_id: int, user: User = Depends(auth_service.get_current_user),db: Session = Depends(get_db)):
    contact = await repository_contacts.update_contact(contact_id,user, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(contact_id: int, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    contact = await repository_contacts.remove_contact(contact_id, user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
