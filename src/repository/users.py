from typing import List, Type

from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel
from src.database.db import get_db



async def get_user_by_email(email: str, db: Session) -> User:
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user associated with that email. If no such user exists,
    it will return None.

    :param email: str: Specify the type of parameter that is expected to be passed into the function
    :param db: Session: Pass the database session to the function
    :return: The first user in the database with a given email address
    :doc-author: OSA
    """
    return db.query(User).filter(User.email == email).first()


async def bun_user_by_id(user_id: int, db: Session) -> Type[User]:
    """
    The bun_user_by_id function takes in a user_id and db, and returns the banned user.
        It first checks if the user exists, then sets their banned status to True.
        Finally it commits this change to the database.

    :param user_id: int: Specify the user_id of the user we want to bun
    :param db: Session: Pass in the database session
    :return: A user object if the user exists in the database
    :doc-author: OSA
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.bunned = True
        db.commit()
        return user


async def unbun_user_by_id(user_id: int, db: Session) -> Type[User]:
    """
    The unban_user_by_id function takes a user_id and db as arguments.
    It then queries the database for a User with that id, and if it finds one, sets its banned attribute to False.
    Finally, it commits the change to the database.

    :param user_id: int: Identify the user to be unbanned
    :param db: Session: Access the database
    :return: The user object
    :doc-author: OSA
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.bunned = False
        db.commit()
        return user

def get_user_by_bunned_field() -> List[User]:
    """
    The get_user_by_banned_field function returns a list of all users who have been banned.

    :return: A list of all users who have been banned
    :doc-author: OSA
    """
    db = next(get_db())
    return db.query(User).filter(User.bunned == True).all()


async def create_user(body: UserModel, db: Session, client_ip) -> User:
    """
    The create_user function creates a new user in the database.
        Args:
            body (UserModel): The UserModel object containing the data to be inserted into the database.
            db (Session): The SQLAlchemy Session object used to interact with our PostgreSQL database.

    :param body: UserModel: Pass the user data to the function
    :param db: Session: Access the database
    :param client_ip: Store the ip address of the user
    :return: The newly created user
    :doc-author: OSA
    """
    print(body)
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()

    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar, ip=client_ip)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Identify the user in the database
    :param token: str | None: Update the refresh token in the database
    :param db: Session: Access the database
    :return: Nothing, so it should be annotated as -&gt; none
    :doc-author: OSA
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.


    :param email: str: Get the email of the user
    :param db: Session: Pass the database session to the function
    :return: Nothing
    :doc-author: OSA
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user.

    :param email: Find the user in the database
    :param url: str: Specify the type of data that is being passed into the function
    :param db: Session: Pass the database session to the function
    :return: The updated user object
    :doc-author: OSA
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
