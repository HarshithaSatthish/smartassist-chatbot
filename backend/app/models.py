import re
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """Incoming chat message from the frontend."""

    message: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Please enter a message.")
        return cleaned

    @field_validator("conversation_id")
    @classmethod
    def empty_conversation_id(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class ChatResponse(BaseModel):
    """Outgoing chatbot reply."""

    reply: str
    source: Literal["predefined", "ai"]
    conversation_id: str


class HealthResponse(BaseModel):
    status: str
    service: str


class AuthRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)

    @field_validator("username")
    @classmethod
    def username_must_be_valid(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Please enter a username.")
        if len(cleaned) < 3:
            raise ValueError("Username must be at least 3 characters.")
        if len(cleaned) > 32:
            raise ValueError("Username must be at most 32 characters.")
        if not re.fullmatch(r"[A-Za-z0-9_]+", cleaned):
            raise ValueError("Username can only use letters, numbers, and underscores.")
        return cleaned

    @field_validator("password")
    @classmethod
    def password_must_be_valid(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Please enter a password.")
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters.")
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password is too long.")
        return value


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


class UserResponse(BaseModel):
    username: str


class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str


class ChatMessage(BaseModel):
    role: Literal["user", "bot"]
    content: str
    timestamp: str


class ConversationDetail(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    messages: list[ChatMessage]


class DeleteResponse(BaseModel):
    ok: bool
