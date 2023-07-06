from datetime import date, datetime
# from typing import List, Optional
#
# import pydantic
from pydantic import BaseModel, Field, EmailStr


class ContactBase(BaseModel):
    """
    Represents the base model for a contact.

    Attributes:
        firstname (str): The first name of the contact. Maximum length is 50 characters.
        lastname (str): The last name of the contact. Maximum length is 50 characters.
        phone_number (str): The phone number of the contact. Maximum length is 50 characters.
        email (str): The email address of the contact. Maximum length is 50 characters.
        date_of_birth (date): The date of birth of the contact.
        description (str): A description or additional information about the contact. Maximum length is 150 characters.
    """
    firstname: str = Field(max_length=50)
    lastname: str = Field(max_length=50)
    phone_number: str = Field(max_length=50)
    email: str = Field(max_length=50)
    date_of_birth: date
    description: str = Field(max_length=150)


class ContactUpdate(ContactBase):
    """
    Represents the model for updating a contact.

    Attributes:
        firstname (str): The updated first name of the contact. Maximum length is 50 characters.
        lastname (str): The updated last name of the contact. Maximum length is 50 characters.
        phone_number (str): The updated phone number of the contact. Maximum length is 50 characters.
        email (str): The updated email address of the contact. Maximum length is 50 characters.
        date_of_birth (date): The updated date of birth of the contact.
        description (str): The updated description or additional information about the contact.
        Maximum length is 150 characters.
    """
    firstname: str = Field(max_length=50)
    lastname: str = Field(max_length=50)
    phone_number: str = Field(max_length=50)
    email: str = Field(max_length=50)
    date_of_birth: date
    description: str = Field(max_length=150)


class ContactResponse(ContactBase):
    """
    Represents the model for a contact response.

    Attributes:
        id (int): The unique identifier of the contact.
        created_at (date): The date when the contact was created.
        firstname (str): The first name of the contact. Maximum length is 50 characters.
        lastname (str): The last name of the contact. Maximum length is 50 characters.
        phone_number (str): The phone number of the contact. Maximum length is 50 characters.
        email (str): The email address of the contact. Maximum length is 50 characters.
        date_of_birth (date): The date of birth of the contact.

    Config:
        orm_mode (bool): Indicates that the model is used in ORM mode for database operations.
    """
    id: int
    created_at: date
    firstname: str = Field(max_length=50)
    lastname: str = Field(max_length=50)
    phone_number: str = Field(max_length=50)
    email: str = Field(max_length=50)
    date_of_birth: date

    class Config:
        orm_mode = True


class UserModel(BaseModel):
    """
    Represents a user model.

    Attributes:
        username (str): The username of the user. Must have a minimum length of 2
        characters and a maximum length of 40 characters.
        email (EmailStr): The email address of the user.
        password (str): The password of the user. Must have a minimum length of 6
        characters and a maximum length of 20 characters.
    """
    username: str = Field(min_length=2, max_length=40)
    email: EmailStr
    password: str = Field(min_length=6, max_length=20)


class UserDb(BaseModel):
    """
   Represents a user model retrieved from the database.

   Attributes:
       id (int): The unique identifier of the user.
       username (str): The username of the user.
       email (str): The email address of the user.
       created_at (datetime): The timestamp when the user was created.
       avatar (str): The URL or path to the user's avatar.

   Config:
       orm_mode (bool): Indicates that the model is used in ORM mode for database operations.
    """
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    """
    Represents the response model for a user.

    Attributes:
        user (UserDb): The user model containing user information.
        detail (str): The detail message indicating the status of the user operation.
        Default is "User successfully created".
    """
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    """
        Represents a token model.

        Attributes:
            access_token (str): The access token.
            refresh_token (str): The refresh token.
            token_type (str): The token type. Default is "bearer".
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """
    Represents a request model for an email.

    Attributes:
        email (EmailStr): The email address.

    """
    email: EmailStr
