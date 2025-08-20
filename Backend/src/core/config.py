
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    APP_NAME: str = Field(default="CineStream Backend", description="Application name.")
    APP_VERSION: str = Field(default="1.0.0", description="Application version.")
    ENV: str = Field(default="development", description="Environment name.")
    CORS_ALLOW_ORIGINS: str = Field(
        # Important: Avoid using "*" when allow_credentials=True in CORSMiddleware.
        # Default to the running Frontend origin and common local dev origins.
        default="https://vscode-internal-14938-beta.beta01.cloud.kavia.ai:4000,http://localhost:4000,http://127.0.0.1:4000",
        description="Comma separated list of allowed origins for CORS.",
    )

    # Auth / JWT
    JWT_SECRET: str = Field(default="change-me", description="JWT secret for signing tokens.")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm.")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, description="Access token expiry in minutes.")

    # Database
    DATABASE_URL: Optional[str] = Field(default=None, description="Full DB URL.")
    DB_HOST: Optional[str] = Field(default=None, description="Database host.")
    DB_PORT: Optional[int] = Field(default=None, description="Database port.")
    DB_NAME: Optional[str] = Field(default=None, description="Database name.")
    DB_USER: Optional[str] = Field(default=None, description="Database user.")
    DB_PASSWORD: Optional[str] = Field(default=None, description="Database password.")

    # Payments (optional real gateway keys; we simulate payments by default)
    STRIPE_API_KEY: Optional[str] = Field(default=None, description="Stripe API key.")
    PAYPAL_CLIENT_ID: Optional[str] = Field(default=None, description="PayPal client id.")
    PAYPAL_CLIENT_SECRET: Optional[str] = Field(default=None, description="PayPal client secret.")
    UPI_PROVIDER: str = Field(default="mock", description="UPI provider (mock/razorpay/etc).")

    class Config:
        env_file = ".env"
        case_sensitive = True

    # PUBLIC_INTERFACE
    def cors_allowed_origins(self) -> List[str]:
        """Return CORS allowed origins as list, splitting by comma and stripping whitespace."""
        if not self.CORS_ALLOW_ORIGINS:
            return ["*"]
        return [o.strip() for o in self.CORS_ALLOW_ORIGINS.split(",") if o.strip()]

    # PUBLIC_INTERFACE
    def assembled_database_url(self) -> str:
        """Get the database URL from env or assemble from components; falls back to local sqlite for dev."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if self.DB_HOST and self.DB_PORT and self.DB_NAME and self.DB_USER and self.DB_PASSWORD:
            return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        # Development-only fallback to allow docs/tests without Postgres
        return "sqlite:///./dev.db"


@lru_cache
# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Return cached settings instance loaded from environment variables."""
    return Settings()
