"""Input validation utilities for security"""
import re
from typing import Optional
from pydantic import validator, field_validator
from fastapi import HTTPException


# Safe string patterns
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
SAFE_NAME_PATTERN = re.compile(r'^[\w\s\-\.\']+$')
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)

# Max lengths for various fields
MAX_NAME_LENGTH = 255
MAX_EMAIL_LENGTH = 255
MAX_CREDENTIALS_LENGTH = 5000
MAX_SYSTEM_PROMPT_LENGTH = 10000
MAX_RESPONSE_LENGTH = 50000
MAX_REASONING_LENGTH = 10000


def validate_email(email: str) -> str:
    """Validate email format"""
    if not email or len(email) > MAX_EMAIL_LENGTH:
        raise ValueError("Invalid email length")
    if not EMAIL_PATTERN.match(email):
        raise ValueError("Invalid email format")
    return email.lower().strip()


def validate_name(name: Optional[str]) -> Optional[str]:
    """Validate name for safe characters"""
    if name is None:
        return None
    name = name.strip()
    if len(name) > MAX_NAME_LENGTH:
        raise ValueError(f"Name too long (max {MAX_NAME_LENGTH} characters)")
    if not SAFE_NAME_PATTERN.match(name):
        raise ValueError("Name contains invalid characters")
    return name


def validate_uuid(uuid_str: str) -> str:
    """Validate UUID format"""
    if not UUID_PATTERN.match(uuid_str):
        raise ValueError("Invalid UUID format")
    return uuid_str


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Sanitize a string by stripping and limiting length"""
    if not value:
        return ""
    value = value.strip()
    if len(value) > max_length:
        value = value[:max_length]
    return value


def sanitize_html_in_string(value: str) -> str:
    """Remove potential HTML/script tags from string
    
    Note: This is a basic sanitization. For full protection,
    use a library like bleach for HTML content.
    """
    if not value:
        return ""
    # Remove script tags and contents
    value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
    # Remove other HTML tags (but keep content)
    value = re.sub(r'<[^>]+>', '', value)
    return value


def validate_system_prompt(prompt: Optional[str]) -> Optional[str]:
    """Validate and sanitize system prompt"""
    if prompt is None:
        return None
    prompt = sanitize_string(prompt, MAX_SYSTEM_PROMPT_LENGTH)
    # System prompts shouldn't contain potential injection attempts
    return prompt


def validate_search_query(query: Optional[str]) -> Optional[str]:
    """Validate search query to prevent SQL injection via LIKE
    
    SQLAlchemy's ORM already parameterizes queries, but we still
    sanitize to prevent other issues.
    """
    if query is None:
        return None
    # Remove SQL special characters used in LIKE
    query = query.replace('%', '').replace('_', '')
    # Limit length
    query = sanitize_string(query, 200)
    return query


class SecurityValidationError(HTTPException):
    """Custom exception for security validation failures"""
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)
