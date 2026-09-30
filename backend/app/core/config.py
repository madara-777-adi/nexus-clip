from pydantic import AliasChoices, Field, ValidationInfo, field_validator
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

    cors_origins_raw: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        validation_alias=AliasChoices(
            "CORS_ORIGINS",
            "ALLOWED_ORIGINS",
            "cors_origins_raw",
        ),
        description=(
            "Comma-separated list of allowed CORS origins (no brackets/quotes "
            "needed). Defaults to Vite (5173) and CRA (3000) dev servers. "
            "Production MUST override via CORS_ORIGINS env var, e.g. "
            "'https://nexusclip.app,https://www.nexusclip.app'."
        ),
    )

    @property
    def cors_origins(self) -> list[str]:
        """Parsed list of allowed origins, trimmed and empty entries dropped."""
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    @field_validator("cors_origins_raw")
    @classmethod
    def validate_production_origins(cls, value: str, info: ValidationInfo) -> str:
        """Reject permissive wildcard CORS origins in production."""
        origins = [origin.strip() for origin in value.split(",")]
        if info.data.get("environment") == "production" and any("*" in origin for origin in origins):
            raise ValueError("Wildcard origins are not allowed when environment is production.")
        return value

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

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, value: str) -> str:
        """Require enough entropy for the JWT signing secret."""
        if len(value) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long.")
        return value

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
    # Object storage
    # ------------------------------------------------------------------

    r2_endpoint_url: str | None = Field(default=None, alias="R2_ENDPOINT_URL")
    r2_access_key_id: str | None = Field(default=None)
    r2_secret_access_key: str | None = Field(default=None)
    r2_bucket_name: str | None = Field(default=None)
    r2_public_url: str | None = Field(default=None)

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


settings = Settings()  # type: ignore
