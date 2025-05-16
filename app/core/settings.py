from typing import Optional

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import URL


class DatabaseSettings(BaseSettings):
    """Database settings."""

    DB_DRIVER: str = "sqlite"
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_NAME: str = "sql_app.db"
    DB_ECHO: bool = False
    DB_POOL_PRE_PING: bool = True
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Build SQLAlchemy database URI."""
        if self.DB_DRIVER == "sqlite":
            return f"sqlite:///{self.DB_NAME}"

        return str(
            URL.create(
                f"{self.DB_DRIVER}://",
                username=self.DB_USER,
                password=self.DB_PASSWORD,
                host=self.DB_HOST,
                port=self.DB_PORT,
                database=self.DB_NAME,
            )
        )


class Settings(BaseSettings):
    """Application settings."""

    # Application
    PROJECT_NAME: str = "Mini DNS API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # CORS
    CORS_ORIGINS: list[str] = ["*"]
    CORS_METHODS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]
    CORS_CREDENTIALS: bool = True

    # Database
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)

    # Convenience properties
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Get SQLAlchemy database URI."""
        return self.db.SQLALCHEMY_DATABASE_URI

    @property
    def SQL_ECHO(self) -> bool:
        """Get SQL echo setting."""
        return self.db.DB_ECHO

    @property
    def SQL_POOL_PRE_PING(self) -> bool:
        """Get SQL pool pre-ping setting."""
        return self.db.DB_POOL_PRE_PING

    @property
    def SQL_POOL_SIZE(self) -> int:
        """Get SQL pool size."""
        return self.db.DB_POOL_SIZE

    @property
    def SQL_MAX_OVERFLOW(self) -> int:
        """Get SQL max overflow."""
        return self.db.DB_MAX_OVERFLOW

    @property
    def SQL_POOL_TIMEOUT(self) -> int:
        """Get SQL pool timeout."""
        return self.db.DB_POOL_TIMEOUT

    # Validators
    @field_validator("ENVIRONMENT")
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of: development, testing, production."""
        if v not in ("development", "testing", "production"):
            raise ValueError("ENVIRONMENT must be one of: development, testing, production")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
        case_sensitive=True,
    )


# Create settings instance
settings = Settings()
