from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from contextlib import contextmanager

from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.database.models import User
from src.services.email_service import auth_service
from src.logger import get_logger

# from tests.test_routes_contacts import token

logger = get_logger(__name__)


@pytest.fixture()
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.services.email_service.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]


def test_create_user(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.services.email_service.send_email", mock_send_email)
    response = client.post("/api/auth/signup", json=user).json()

    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()

    assert user.get('username') == response.get('user').get('username')


def test_user_ip_checker(client, user, session, monkeypatch, client_ip="127.0.0.1"):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.services.email_service.send_email", mock_send_email)

    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 409
    assert response.json().get('detail') == 'Account already exists'
    logger.info(response)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    current_user.ip = client_ip
    assert current_user.ip == client_ip
    session.commit()

    # assert current_user.ip == response.get('user').get('ip')
    # assert current_user.ip == 'localhost'


def test_login_func(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    assert data.get("token_type") == 'bearer'
    assert response.status_code == 200


def test_login_wrong_email(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": 'wrong-email@gmail.com', "password": user.get('password')},
    )
    logger.info(response)
    assert response.status_code == 401
    assert response.json().get('detail') == "Invalid email"


def test_login_wrong_password(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": 'wrongpass'},
    )
    logger.info(response)
    assert response.status_code == 401
    assert response.json().get('detail') == "Invalid password"



def test_invalid_refresh_token(client, session, user, token, monkeypatch):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    mock_user_by_email = AsyncMock(return_value=current_user)
    monkeypatch.setattr("src.repository.users.get_user_by_email", mock_user_by_email)
    mock_update_token = AsyncMock(return_value=token)
    monkeypatch.setattr("src.repository.users.update_token", mock_update_token)
    mock_create_access_token = AsyncMock(return_value="new-token")
    monkeypatch.setattr("src.services.auth.Auth.create_access_token", mock_create_access_token)
    mock_create_refresh_token = AsyncMock(return_value="new-refresh-token")
    monkeypatch.setattr("src.services.auth.Auth.create_refresh_token", mock_create_refresh_token)
    mock_decode_refresh_token = AsyncMock(return_value='decoded-refresh-token')
    monkeypatch.setattr("src.services.auth.Auth.decode_refresh_token", mock_decode_refresh_token)
    response = client.get("/api/auth/refresh_token", headers={'Authorization': f"Bearer {token}"})


    old_tkn = current_user.refresh_token
    logger.info(response.text)
    assert response.json().get('refresh_token') != old_tkn
    assert response.status_code == 401
    assert response.json().get('detail') == "Invalid refresh token"


def test_refresh_token(client, session, user, token, monkeypatch):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    mock_user_by_email = AsyncMock(return_value=current_user)
    monkeypatch.setattr("src.repository.users.get_user_by_email", mock_user_by_email)
    mock_update_token = AsyncMock(return_value=token)
    monkeypatch.setattr("src.repository.users.update_token", mock_update_token)
    mock_create_access_token = AsyncMock(return_value="new-token")
    monkeypatch.setattr("src.services.auth.Auth.create_access_token", mock_create_access_token)
    mock_create_refresh_token = AsyncMock(return_value="new-refresh-token")
    monkeypatch.setattr("src.services.auth.Auth.create_refresh_token", mock_create_refresh_token)
    mock_decode_refresh_token = AsyncMock(return_value='decoded-refresh-token')
    monkeypatch.setattr("src.services.auth.Auth.decode_refresh_token", mock_decode_refresh_token)
    response = client.get("/api/auth/refresh_token", headers={'Authorization': f"Bearer {current_user.refresh_token}"})
    logger.info(response.text)

    """return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}"""
    assert response.json().get('access_token') == mock_create_access_token.return_value
    assert response.json().get('refresh_token') == mock_create_refresh_token.return_value
    assert response.json().get('token_type') == "bearer"



def test_confirmed_email(token, session, client, user, monkeypatch):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = False
    session.commit()

    mock_get_email_from_token = AsyncMock(return_value=user.get('email'))
    monkeypatch.setattr("src.services.auth.Auth.get_email_from_token", mock_get_email_from_token)
    mock_get_user_by_email = AsyncMock(return_value=current_user)
    monkeypatch.setattr("src.repository.users.get_user_by_email", mock_get_user_by_email)
    mock_confirmed_email = AsyncMock(return_value=current_user.confirmed)
    monkeypatch.setattr("src.repository.users.confirmed_email", mock_confirmed_email)


    response = client.get(f"/api/auth/confirmed_email/{token}")
    logger.info(response.text)
    detail = "Verification error"

    assert response.status_code == 200
    assert response.json().get('message') == "Email confirmed"


def test_already_was_confirmed_email(token, session, client, user, monkeypatch):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()

    mock_get_email_from_token = AsyncMock(return_value=user.get('email'))
    monkeypatch.setattr("src.services.auth.Auth.get_email_from_token", mock_get_email_from_token)
    mock_get_user_by_email = AsyncMock(return_value=current_user)
    monkeypatch.setattr("src.repository.users.get_user_by_email", mock_get_user_by_email)
    mock_confirmed_email = AsyncMock(return_value=current_user.confirmed)
    monkeypatch.setattr("src.repository.users.confirmed_email", mock_confirmed_email)


    response = client.get(f"/api/auth/confirmed_email/{token}")
    logger.info(response.text)


    assert response.status_code == 200
    assert response.json().get('message') == "Your email is already confirmed"


def test_not_confirmed_email_yet(token, session, client, user, monkeypatch):
    current_user: User = session.query(User).filter(User.email == 'wrong@email.com').first()

    mock_get_email_from_token = AsyncMock(return_value=user.get('email'))
    monkeypatch.setattr("src.services.auth.Auth.get_email_from_token", mock_get_email_from_token)
    mock_get_user_by_email = AsyncMock(return_value=current_user)
    monkeypatch.setattr("src.repository.users.get_user_by_email", mock_get_user_by_email)
    mock_confirmed_email = AsyncMock(return_value=current_user.confirmed if current_user else None)
    monkeypatch.setattr("src.repository.users.confirmed_email", mock_confirmed_email)


    response = client.get(f"/api/auth/confirmed_email/{token}")
    logger.info(response.text)


    assert response.status_code == 400
    assert response.json().get('detail') == "Verification error"




def test_login_email_confirmation(client, user, session):
    current_user = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = False
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    logger.info(response)

    assert response.status_code == 401
    assert response.json().get('detail') == "Email not confirmed"
    current_user.confirmed = True
    session.commit()
