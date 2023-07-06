from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import settings

print(settings.mail_username, type(settings.mail_username))
conf = ConnectionConfig(
    MAIL_USERNAME=str(settings.mail_username),
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_username,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="REST Application Service",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)
"""
Represents the configuration for connecting to a mail server.

Attributes:
    MAIL_USERNAME (str): The mail server username.
    MAIL_PASSWORD (str): The mail server password.
    MAIL_FROM (str): The email address to use as the "From" address.
    MAIL_PORT (int): The port number for the mail server.
    MAIL_SERVER (str): The mail server hostname or IP address.
    MAIL_FROM_NAME (str): The display name to use for the "From" address.
    MAIL_STARTTLS (bool): Whether to use STARTTLS for secure communication.
    MAIL_SSL_TLS (bool): Whether to use SSL/TLS for secure communication.
    USE_CREDENTIALS (bool): Whether to use credentials for authentication.
    VALIDATE_CERTS (bool): Whether to validate the server's SSL/TLS certificates.
    TEMPLATE_FOLDER (Path): The path to the folder containing email templates.
"""


async def send_email(email: EmailStr, username: str, host: str):
    """
The send_email function sends an email to the user with a link to confirm their email address.
    The function takes in three parameters:
        -email: EmailStr, the user's email address.
        -username: str, the username of the user who is registering for an account.  This will be used in a greeting message within the body of the email sent to them.
        -host: str, this is where we are hosting our application (i.e., localhost).  This will be used as part of a URL that they can click on within their browser.

:param email: EmailStr: Specify the email address of the recipient
:param username: str: Pass the username to the email template
:param host: str: Pass the host url to the email template
:return: A coroutine, which is an object that can be used to control the execution of a
:doc-author: OSA
"""
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)
