from sqlalchemy import Column, Date, Integer, String, ForeignKey, Boolean
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class Contact(Base):
    """
        Represents a contact in the application.

        Attributes:
            id (int): The unique identifier of the contact.
            firstname (str): The first name of the contact.
            lastname (str): The last name of the contact.
            email (str): The email address of the contact.
            phone_number (str): The phone number of the contact.
            date_of_birth (datetime.date): The date of birth of the contact.
            description (str): A description or additional information about the contact.
            created_at (datetime.datetime): The timestamp when the contact was created.
            user_id (int): The foreign key referencing the user associated with the contact.

        Relationships:
            user (User): The user associated with the contact.

        Properties:
            formatted_date_of_birth (str): The formatted date of birth in "dd-mm-yyyy" format. Returns None if date_of_birth is not set.
        """
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    firstname = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    phone_number = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    description = Column(String(150), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'), default=None)

    user = relationship("User", backref='contacts')

    @property
    def formatted_date_of_birth(self):
        """
        The formatted_date_of_birth function returns the date of birth in a formatted string.
        If there is no date of birth, it returns None.

        :param self: Represent the instance of the object itself
        :return: The date of birth in the format dd-mm-yyyy
        :doc-author: OSA
        """
        if self.date_of_birth:
            return self.date_of_birth.strftime("%d-%m-%Y")
        return None


class User(Base):
    """
        Represents a user in the application.

        Attributes:
            id (int): The unique identifier of the user.
            username (str): The username of the user.
            email (str): The email address of the user.
            password (str): The password of the user.
            created_at (datetime.datetime): The timestamp when the user was created.
            avatar (str): The URL or path to the user's avatar.
            refresh_token (str): The refresh token for the user's authentication.
            confirmed (bool): Indicates if the user's email has been confirmed.
            banned (bool): Indicates if the user is banned.
            ip (str): The IP address associated with the user.

        Relationships:
            None

        Properties:
            None
        """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(150), nullable=False, unique=False)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    bunned = Column(Boolean, default=False)
    ip = Column(String, unique=False, default="localhost")


