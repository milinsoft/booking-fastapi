from typing import Literal, dataclass_transform

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


@dataclass_transform()
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    MODE: Literal["DEV", "TEST", "PROD"]
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    # Database
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    TEST_DB_NAME: str

    @computed_field
    def is_test_mode(self) -> bool:
        return self.MODE == "TEST"

    @computed_field
    def DB_URL(self) -> str:  # noqa N802
        db_name = self.TEST_DB_NAME if self.is_test_mode else self.DB_NAME
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}/{db_name}"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str
    # Cache
    REDIS_HOST_URL: str
    REDIS_PORT: str
    # SMTP
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str

    # Sentry
    SENTRY_DSN: str


settings = Settings()
