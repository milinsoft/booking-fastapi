from typing import Literal

from pydantic import computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import NullPool


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    MODE: Literal["DEV", "TEST", "PROD"]
    # Database
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    TEST_DB_NAME: str

    @computed_field
    def DB_URL(self) -> str:  # noqa N802
        db_name = self.TEST_DB_NAME if self.is_test_mode() else self.DB_NAME
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}/{db_name}"

    @computed_field
    def DB_PARAMS(self) -> dict:
        return {"poolclass": NullPool} if self.is_test_mode() else {}

    # JWT
    SECRET_KEY: str
    ALGORITHM: str
    # Cache
    REDIS_HOST_URL: str
    REDIS_PORT: str
    # SMTP
    SMTP_HOST: str
    SMTP_PORT: str
    SMTP_USER: str
    SMTP_PASSWORD: str

    def is_test_mode(self) -> bool:
        return self.MODE == "TEST"


settings = Settings()
