"""Схемы."""
from pydantic import BaseModel


class TokenSchema(BaseModel):
    """Схема токенов."""

    access_token: str
    refresh_token: str


class UserLoginSchema(BaseModel):
    """Схема логина."""

    login: str
    password: str
