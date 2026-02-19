"""Application configuration"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Database (raw URL from environment, may use postgres:// scheme)
    DATABASE_URL_RAW: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/gcb",
        validation_alias="DATABASE_URL"
    )
    
    @property
    def DATABASE_URL(self) -> str:
        """Convert postgres:// to postgresql:// for SQLAlchemy 2.0+ compatibility.
        
        Railway and Heroku provide DATABASE_URL with postgres:// scheme,
        but SQLAlchemy 2.0+ only accepts postgresql://
        """
        url = self.DATABASE_URL_RAW
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url
    
    # NextAuth
    NEXTAUTH_SECRET: str = ""
    
    # CORS (stored as string, parsed to list)
    CORS_ORIGINS_STR: str = "http://localhost:3000,http://localhost:3001,https://frontend-production-8b79.up.railway.app,https://greatcommissionbenchmark.ai,https://www.greatcommissionbenchmark.ai"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",") if origin.strip()]
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # OpenRouter
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_REFERER: str = "https://greatcommissionbenchmark.ai"
    
    # Note: Runner API keys are now per-user and stored in the database
    # See UserAPIKey model - users generate keys from their dashboard
    
    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # Development Mode - bypasses actual payment processing
    # Set to True for local development without Stripe
    PAYMENT_DEV_MODE: bool = False
    
    # Email (Resend)
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "Great Commission Benchmark <noreply@greatcommissionbenchmark.ai>"
    
    # Newsletter (MailerLite)
    MAILERLITE_API_KEY: str = ""
    MAILERLITE_GROUP_ID: str = ""  # Optional: specific subscriber group ID
    
    # S3-Compatible Storage (Railway Simple Storage or AWS S3)
    S3_ACCESS_KEY_ID: str = ""
    S3_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET: str = ""
    S3_ENDPOINT_URL: str = ""  # Railway: set to endpoint URL, AWS: leave empty
    S3_REGION: str = "us-east-1"
    
    # Backend public URL for generating file proxy URLs
    # Railway buckets are private, so files are served through /api/files/{path}
    BACKEND_PUBLIC_URL: str = "http://localhost:8001"
    
    # Redis (optional) — when set, leaderboard and public caches use Redis
    # so they persist across restarts and deploys.
    # Railway: add a Redis service and set REDIS_URL to its connection string.
    # Leave empty to use the in-memory cache (default for local dev).
    REDIS_URL: str = ""

    # Google reCAPTCHA v3
    RECAPTCHA_SECRET_KEY: str = ""
    RECAPTCHA_SITE_KEY: str = ""  # For reference, not used in backend
    RECAPTCHA_ENABLED: bool = True  # Can be disabled for development
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
