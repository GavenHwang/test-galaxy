import os
import secrets
import string
import typing
from typing import ClassVar
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    VERSION: str = "0.1.0"
    APP_TITLE: str = "Vue FastAPI Admin"
    PROJECT_NAME: str = "Vue FastAPI Admin"
    APP_DESCRIPTION: str = "Description"

    CORS_ORIGINS: typing.List = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: typing.List = ["*"]
    CORS_ALLOW_HEADERS: typing.List = ["*"]

    DEBUG: bool = True

    PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    BASE_DIR: str = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir))
    LOGS_ROOT: str = os.path.join(BASE_DIR, "app/logs")
    SECRET_KEY: str = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 day
    TORTOISE_ORM: dict = {
        "connections": {

            # MySQL/MariaDB configuration
            # Install with: tortoise-orm[asyncmy]
            "mysql": {
                "engine": "tortoise.backends.mysql",
                "credentials": {
                    "host": "127.0.0.1",  # Database host address
                    "port": 3306,  # Database port
                    "user": "yaoshuai",  # Database username
                    "password": "yaoshuai",  # Database password
                    "database": "platform",  # Database name
                },
            }
        },
        "apps": {
            "models": {
                "models": ["app.models", "aerich.models"],
                "default_connection": "mysql",
            },
        },
        "use_tz": False,  # Whether to use timezone-aware datetimes
        "timezone": "Asia/Shanghai",  # Timezone setting
    }
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    LOGLEVEL: ClassVar[str] = 'DEBUG'
    TOKEN_TIME: int = 24 * 60


settings = Settings()
