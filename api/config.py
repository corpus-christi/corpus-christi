import os
from typing import Optional
from pydantic_settings import BaseSettings

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Settings(BaseSettings):
    # Database — set DATABASE_URL directly to override all PSQL_* vars
    DATABASE_URL: Optional[str] = None
    PSQL_USER: str = "postgres"
    PSQL_PASS: str = "postgres"
    PSQL_HOST: str = "localhost"
    PSQL_DB: Optional[str] = None
    CC_ENV: str = "dev"

    # Security
    JWT_SECRET_KEY: str = "change-me-in-production"
    SECRET_KEY: str = "change-me-in-production"

    # Mail
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 465
    MAIL_USE_TLS: bool = False
    MAIL_USE_SSL: bool = True
    MAIL_SUPPRESS_SEND: bool = False

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if self.PSQL_DB:
            db_name = self.PSQL_DB
        elif self.CC_ENV == "test":
            db_name = "cc-test"
        elif self.CC_ENV == "staging":
            db_name = "cc-staging"
        elif self.CC_ENV == "prod":
            db_name = "cc-prod"
        else:
            db_name = "cc-dev"
        return f"postgresql://{self.PSQL_USER}:{self.PSQL_PASS}@{self.PSQL_HOST}/{db_name}"

    @property
    def debug(self) -> bool:
        return self.CC_ENV in ("dev", "test")

    @property
    def testing(self) -> bool:
        return self.CC_ENV == "test"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
