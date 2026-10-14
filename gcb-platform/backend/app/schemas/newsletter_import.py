"""Bounded, preview-first subscriber imports."""
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class NewsletterImportRequest(BaseModel):
    csv_content: str = Field(min_length=1, max_length=2_000_000)
    source: str = Field(min_length=1, max_length=120)
    email_column: str | None = Field(default=None, max_length=255)
    name_column: str | None = Field(default=None, max_length=255)
    status_column: str | None = Field(default=None, max_length=255)
    consent_note: str = Field(default="", max_length=1000)
    confirm_subscribed: bool = False
    dry_run: bool = True

    @field_validator("source", "consent_note")
    @classmethod
    def trim_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("source")
    @classmethod
    def require_source(cls, value: str) -> str:
        if not value:
            raise ValueError("Describe where these subscribers came from")
        return value


class NewsletterImportRow(BaseModel):
    row: int
    email: str
    action: Literal["create_active", "create_unsubscribed", "unsubscribe", "unchanged", "protected", "duplicate", "invalid"]
    message: str


class NewsletterImportResponse(BaseModel):
    dry_run: bool
    batch_id: UUID | None = None
    columns: list[str]
    total_rows: int
    counts: dict[str, int]
    rows: list[NewsletterImportRow]
    rows_truncated: bool
    requires_consent: bool
    message: str


class MailerLiteImportRequest(BaseModel):
    dry_run: bool = True
    snapshot_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    confirm_subscribed: bool = False
    consent_note: str = Field(default="", max_length=1000)
