from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    app_name: str = Field(
        default="Nexus Clip",
        description="Application name",
    )

    app_version: str = Field(
        default="1.0.0",
        description="Application version",
    )

    debug: bool = Field(
        default=False,
        description="Debug mode",
    )

    environment: str = Field(
        default="development",
        description="Environment (development, staging, production)",
    )

    # ------------------------------------------------------------------
    # Server
    # ------------------------------------------------------------------

    host: str = Field(
        default="0.0.0.0",
        description="Server host",
    )

    port: int = Field(
        default=8000,
        description="Server port",
    )

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------

    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins",
    )

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )

    log_format: str = Field(
        default="json",
        description="Log format (json or text)",
    )

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    database_url: str = Field(
        description=(
            "PostgreSQL async database URL "
            "(e.g. postgresql+psycopg://user:password@localhost:5432/nexus_clip)"
        ),
    )

    # ------------------------------------------------------------------
    # Google OAuth
    # ------------------------------------------------------------------

    google_client_id: str = Field(
        description="Google OAuth Client ID",
    )

    # ------------------------------------------------------------------
    # JWT
    # ------------------------------------------------------------------

    jwt_secret_key: str = Field(
        description="Secret used to sign JWT access tokens",
    )

    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm",
    )

    jwt_expire_minutes: int = Field(
        default=60,
        description="JWT access token lifetime in minutes",
    )

    # ------------------------------------------------------------------
    # Redis
    # ------------------------------------------------------------------

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )

    redis_enabled: bool = Field(
        default=True,
        description="Enable Redis caching",
    )

    cache_default_ttl: int = Field(
        default=3600,
        description="Default cache TTL in seconds",
    )

    # ------------------------------------------------------------------
    # Upload
    # ------------------------------------------------------------------

    max_upload_size_mb: int = Field(
        default=25,
        description="Maximum allowed upload file size in megabytes",
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"


settings = Settings()
