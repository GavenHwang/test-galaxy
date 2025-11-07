import os
import secrets
import string
import typing
import platform
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
    # 固定 SECRET_KEY，避免重启后 Token 失效
    # 生产环境应从环境变量或配置文件读取
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'test-galaxy-secret-key-fixed-20241106-do-not-share-in-production')
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 day
    
    # 根据操作系统选择数据库配置
    def get_db_config(self):
        system = platform.system().lower()
        if system == "linux":
            # Linux配置
            return {
                "host": "10.0.36.102",  # Database host address
                "port": 3309,  # Database port
                "user": "root",  # Database username
                "password": "root123",  # Database password
                "database": "test-galaxy",  # Database name
            }
        elif system == "windows":
            # Windows配置
            return {
                "host": "127.0.0.1",  # Database host address
                "port": 3306,  # Database port
                "user": "yaoshuai",  # Database username
                "password": "yaoshuai",  # Database password
                "database": "platform",  # Database name
            }
        elif system == "darwin":  # macOS
            # macOS配置
            return {
                "host": "127.0.0.1",  # Database host address
                "port": 3306,  # Database port
                "user": "root",  # Database username
                "password": "Haha123456.",  # Database password
                "database": "test-galaxy",  # Database name
            }
        else:
            # 默认配置
            return {
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "root123",
                "database": "test-galaxy",
            }
    
    TORTOISE_ORM: dict = {
        "connections": {
            # MySQL/MariaDB configuration
            # Install with: tortoise-orm[asyncmy]
            "mysql": {
                "engine": "tortoise.backends.mysql",
                "credentials": {},  # 将在 __init__ 中设置
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
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 设置数据库配置
        self.TORTOISE_ORM["connections"]["mysql"]["credentials"] = self.get_db_config()

    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    LOGLEVEL: ClassVar[str] = 'DEBUG'
    TOKEN_TIME: int = 24 * 60


settings = Settings()