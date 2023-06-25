from datetime import date, datetime
from typing import List, Optional

import pydantic
from pydantic import BaseModel, Field, EmailStr


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


#Create
class UserModel(BaseModel):
    username: str = Field(min_length=2, max_length=40)
    email: EmailStr
    password: str = Field(min_length=6, max_length=20)


#
class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"