import os
from functools import lru_cache
from typing import Any
from typing import Dict
from typing import Optional

from pydantic import EmailStr
from pydantic import Field
from pydantic import PostgresDsn
from pydantic import field_validator
from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    """Configuration class containing base settings, common for all settings classes"""

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "fastapi_auth"

    FASTAPI_HOST: str = "0.0.0.0"
    FASTAPI_PORT: str = "5555"

    FAKE_EMAIL_SENDER: EmailStr = "fake@mail.com"
    TEST_EMAIL_SENDER: EmailStr = "fastapi.auth.test.email@gmail.com"
    TEST_EMAIL_APP_PASSWORD: str = "tvyk uqan tzml pmro"

    # # JWT
    JWT_SECRET_KEY: str = "5a161ad692d98ddaf0be7e424d8e9a3df1c177366db830ddfd3eac54093dc671"

    JWT_SECRET_KEY_REFRESH: str = "bc82de5e12a1646cf48e2de22b390de99946b340b7a2eef9efbe260440b9a13b"

    PRE_TFA_SECRET_KEY: str = "cd70cd42957aa7d88f234f33214d8b9c57dd86b9c65293a655c3063cda98c86b"

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 h

    # # 2 FACTOR AUTHENTICATION
    FERNET_KEY_TFA_TOKEN: str = "J_TYpprFmoLlVM0MNZElt8IwEkvEEhAwCmb8P_f7Fro="
    PRE_TFA_TOKEN_EXPIRE_MINUTES: int = 2
    TFA_BACKUP_TOKENS_NR: int = 5
    TFA_TOKEN_LENGTH: int = 6
    TOTP_ISSUER_NAME: str = "fastapi_auth"
    # default tolerance = 30 sec
    # this number is multiplied for 30 sec to increase it.
    # -->MAX = 10 => 5 minutes
    TOTP_TOKEN_TOLERANCE: int = Field(default=2, gt=0, le=10)

    # # CORS
    BACKEND_CORS_ORIGINS: str = "http://localhost:5555"

    # # DB
    SQLALCHEMY_DATABASE_URI: str = "postgresql+asyncpg://admin:admin@fastapi_auth-db:5432/postgres"

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Test that the database connection is present before proceeding with loading the settings"""
        if v is None:
            raise ValueError(v)
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    # # CELERY
    CELERY_BROKER_URL: str = "redis://default:password@redis:6379/0"
    result_backend: str = "redis://default:password@redis:6379/0"
    CELERY_WORKER_PREFETCH_MULTIPLIER: int = 1
    # Celery ACK the queue only when task is completed
    CELERY_TASK_ACKS_LATE: bool = True
    imports: tuple[str] = ("fastapi_auth.tasks.tasks",)
    task_serializer: str = "json"
    accept_content: tuple[str] = ("json",)

    class Config:
        """Additional parameters relevant to config's setup storage"""

        case_sensitive = True


class DevelopmentConfig(BaseConfig):
    """Configuration class containing development settings"""

    LOGGING_LEVEL: str = "DEBUG"


class ProductionConfig(BaseConfig):
    """Configuration class containing production settings"""

    LOGGING_LEVEL: str = "INFO"


class TestingConfig(BaseConfig):
    """Configuration class containing testing settings"""

    # define new attributes with respect to BaseConfig
    DATABASE_CONNECT_DICT: dict = {"check_same_thread": False}
    LOGGING_LEVEL: str = "DEBUG"
    SQLALCHEMY_DATABASE_TEST_SYNC_URI: str = "sqlite:///tests/test_db.db"

    # celery test config
    task_always_eager: bool = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # override attributes of BaseConfig
        # https://fastapi.tiangolo.com/advanced/testing-database/
        self.SQLALCHEMY_DATABASE_URI: str = "sqlite+aiosqlite:///tests/test_db.db"


@lru_cache()
def get_settings():
    """Return settings based on the selected mode"""
    config_cls_dict = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }

    config_name = os.environ.get("FASTAPI_CONFIG", "development")
    print(f"Running app in **{config_name}** mode")
    config_cls = config_cls_dict[config_name]
    return config_cls()


print(os.environ)

settings = get_settings()
