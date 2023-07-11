from pydantic import BaseSettings


class Settings(BaseSettings):
    """Configuration settings for the application."""
    sqlalchemy_database_url: str = 'postgresql+psycopg2://postgres:password@localhost:5432/test-db'
    secret_key: str = 'test'
    algorithm: str = 'test'
    mail_username: str = 'test'
    mail_password: str = 'test'
    mail_from: str = 'test'
    mail_port: int = 465
    mail_server: str = 'test'
    redis_host: str = 'localhost'
    redis_port: int = 6379
    cloudinary_name: str = 'test'
    cloudinary_api_key: str = 'test'
    cloudinary_api_secret: str = 'test'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
