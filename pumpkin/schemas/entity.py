"""Схемы."""
import uuid
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class TokenSchema(BaseModel):
    """Схема токенов."""

    access_token: str
    refresh_token: str


class UserLoginSchema(BaseModel):
    """Схема логина."""

    login: str
    password: str


class RoleSimpleSchema(BaseModel):
    """Схема для реквеста."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str


class UserRoleSchema(BaseModel):
    """Схема для реквеста."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    first_name: str
    last_name: str

    roles: Optional[List[RoleSimpleSchema]] = None
