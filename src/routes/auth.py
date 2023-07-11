from typing import List

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.config.config import settings
from src.database.db import get_db
from src.database.models import User
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail, UserDb
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email_service import send_email


router = APIRouter(prefix='/auth', tags=["Authentication"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    The signup function creates a new user in the database.

    :param body: UserModel: Get the user's email and password from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the client's ip address
    :param db: Session: Pass the database session to the function
    :return: A dictionary with the user and a detail message
    :doc-author: OSA
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    client_ip = request.headers.get("X-Forwarded-For")
    if client_ip:
        # If multiple IP addresses are present, the client's IP address is usually the first one
        client_ip = client_ip.split(",")[0].strip()
    else:
        client_ip = request.client.host
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db, client_ip)
    background_tasks.add_task(send_email, new_user.email, new_user.username, str(request.base_url))

    return {"user": new_user, "detail": "User successfully created"}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    The login function is used to authenticate a user.
    It takes the username and password from the request body,
    verifies them against the database, and returns an access token if successful.

    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: Session: Get the database session
    :return: A token, which is a string
    :doc-author: OSA
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    The refresh_token function is used to refresh the access token.
    The function takes in a refresh token and returns an access_token, a new refresh_token, and the type of token.
    If there is no valid user associated with the given email address or if there are any errors during decoding
    or creating tokens then an HTTPException will be raised.

    :param credentials: HTTPAuthorizationCredentials: Get the credentials from the http request
    :param db: Session: Get the database session
    :return: A dict with the access_token, refresh_token and token type
    :doc-author: OSA
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
    It takes the token from the URL and uses it to get the user's email address.
    The function then checks if there is a user with that email in our database, and if not, returns an error message.
    If there is a user with that email in our database, we check whether their account has already been confirmed or not.
    If it has been confirmed already, we return another error message saying so; otherwise we call repository_users'
    confirmed_email function which sets the 'confirmed' field of that particular record to

    :param token: str: Get the token from the url
    :param db: Session: Get the database session
    :return: A message if the email is already confirmed or when it's confirmed
    :doc-author: OSA
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    The request_email function is used to send an email to the user with a link that will allow them
    to confirm their account. The function takes in a RequestEmail object, which contains the email of
    the user who wants to confirm their account. It then checks if there is already a confirmed account
    with that email address, and if so returns an error message saying as much. If not, it sends an
    email containing a confirmation link.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background queue
    :param request: Request: Get the base_url of the request
    :param db: Session: Get the database session from the dependency
    :return: A message to the user
    :doc-author: OSA
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}



@router.post("/ban/{user_id}")
async def bun_user_ip_by_id(user_id: int, db: Session = Depends(get_db)):
    """
    The bun_user_ip_by_id function is used to ban a user by their ID.
    The function takes in the user_id as an argument and returns a message indicating that the user was successfully banned.

    :param user_id: int: Get the user_id from the url
    :param db: Session: Access the database
    :return: A message that the user was successfully banned
    :doc-author: OSA
    """
    user = await repository_users.bun_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    return {"message": f"User {user.username} was successfully banned."}


@router.post("/unban/{user_id}")
async def unban_user_ip_by_id(user_id: int, db: Session = Depends(get_db)):
    """
    The unban_user_ip_by_id function is used to unban a user by their ID.
    The function takes in the user_id as an argument and returns a message indicating that the user was successfully unbanned.

    :param user_id: int: Get the user id from the url
    :param db: Session: Pass the database connection to the repository layer
    :return: A message that the user was successfully unbanned
    :doc-author: OSA
    """
    user = await repository_users.unbun_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    return {"message": f"User {user.username} was successfully free for now."}



@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_users_me function is a GET endpoint that returns the current user's information.

    :param current_user: User: Get the current user
    :return: A user object
    :doc-author: OSA
    """
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    """
    The update_avatar_user function is used to update the avatar of a user.
    The function takes in an UploadFile object, which contains the file that will be uploaded to Cloudinary.
    It also takes in a User object, which is obtained from auth_service.get_current_user(). This ensures that only
    authenticated users can access this endpoint and change their own avatars (and not anyone else's). Finally, it
    takes in a Session object for database access.

    :param file: UploadFile: Get the file from the request
    :param current_user: User: Get the user that is currently logged in
    :param db: Session: Access the database
    :return: The updated user object
    :doc-author: OSA
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'Users/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'Users/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
