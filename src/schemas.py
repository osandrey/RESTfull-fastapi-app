from datetime import date
from typing import List
from pydantic import BaseModel, Field


class ContactBase(BaseModel):
    firstname: str = Field(max_length=50)
    lastname: str = Field(max_length=50)
    phone_number: str = Field(max_length=50)
    email: str = Field(max_length=50)
    date_of_birth: date
    description: str = Field(max_length=150)


class ContactUpdate(ContactBase):
    firstname: str = Field(max_length=50)
    lastname: str = Field(max_length=50)
    phone_number: str = Field(max_length=50)
    email: str = Field(max_length=50)
    date_of_birth: date
    description: str = Field(max_length=150)


class ContactResponse(ContactBase):
    id: int
    created_at: date
    firstname: str = Field(max_length=50)
    lastname: str = Field(max_length=50)
    phone_number: str = Field(max_length=50)
    email: str = Field(max_length=50)
    date_of_birth: date

    class Config:
        orm_mode = True