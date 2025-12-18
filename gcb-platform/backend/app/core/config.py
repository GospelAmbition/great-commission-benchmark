"""Application configuration"""
from pydantic_settings import BaseSettings
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
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
