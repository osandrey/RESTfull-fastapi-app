from typing import List, Type

from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel
from src.database.db import get_db



async def get_user_by_email(email: str, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()


async def bun_user_by_id(user_id: int, db: Session) -> Type[User]:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.bunned = True
        db.commit()
        return user


async def unbun_user_by_id(user_id: int, db: Session) -> Type[User]:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.bunned = False
        db.commit()
        return user

def get_user_by_bunned_field() -> List[User]:
    db = next(get_db())
    return db.query(User).filter(User.bunned == True).all()


async def create_user(body: UserModel, db: Session, client_ip) -> User:
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
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
