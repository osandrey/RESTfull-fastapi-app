import sqlite3
from unittest.mock import patch, MagicMock

import pytest
from contextlib import contextmanager
from src.database.models import User
from src.services.email_service import auth_service
from src.logger import get_logger


logger = get_logger(__name__)
logger.debug('Start testing program!')


@contextmanager
def create_connection():
    conn = sqlite3.connect(':memory:')
    yield conn
    conn.rollback()
    conn.close()


data = ("Andrii", "andrii@example.com", "andrii123")


@pytest.fixture
def db_connection():
    with create_connection() as connection:
        yield connection


def test_db_operation(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            username STRING,
            email STRING,
            password STRING
        );
    """)
    cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", data)
    db_connection.commit()
    r = cursor.execute("SELECT username, email, password FROM users")
    assert r.fetchone() == data


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


async def test_read_contacts(client, token):

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        print(data)
        assert isinstance(data, list)
        assert data[0]["name"] == "contacts"
        assert "id" in data[0]


if __name__ == '__main__':
    pytest.main()
