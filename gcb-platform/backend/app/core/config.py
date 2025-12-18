"""Application configuration"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/gcb"
    
    # Auth0
    AUTH0_DOMAIN: str = ""
    AUTH0_CLIENT_ID: str = ""
    AUTH0_CLIENT_SECRET: str = ""
    AUTH0_AUDIENCE: str = ""
    
    # CORS (stored as string, parsed to list)
    CORS_ORIGINS_STR: str = "http://localhost:3000,http://localhost:3001"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",") if origin.strip()]
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # OpenRouter
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_REFERER: str = "https://gcb.app"
    
    # Runner API
    RUNNER_API_KEY: str = ""
    
    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # Email (Resend)
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "Great Commission Benchmark <noreply@gcb.app>"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
