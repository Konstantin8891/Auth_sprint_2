"""Схемы."""
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    """Схема регистрации пользователя."""

    login: str
    password: str
    first_name: str
    last_name: str


class UserInDB(BaseModel):
    """Схема пользователя(ответ)."""

    id: UUID
    first_name: str
    last_name: str

    class Config:
        """Конфиг."""

        orm_mode = True


class TokenSchema(BaseModel):
    """Схема токенов."""

    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


class UserLoginSchema(BaseModel):
    """Схема логина."""

    login: str
    password: str


class RefreshSchema(BaseModel):
    """Схема рефреша."""

    refresh_token: str


class UserPatchSchema(BaseModel):
    """Схема патча пользователя."""

    login: str
    password: str


class SectionCreateSchema(BaseModel):
    """Раздел - создание."""

    name: str


class SectionViewSchema(BaseModel):
    """Раздел - просмотр."""

    id: uuid.UUID
    name: str


class PermissionCreateSchema(BaseModel):
    """Создание пермишена."""

    can_view: bool
    can_edit: bool
    can_delete: bool
    section_id: uuid.UUID


class PermissionViewSchema(BaseModel):
    """Пермишен - просмотр."""

    can_view: bool
    can_edit: bool
    can_delete: bool
    section: SectionViewSchema


class RoleCreateSchema(BaseModel):
    """Роль - создание."""

    name: str
    permissions: List[PermissionCreateSchema]


class RoleViewSchema(BaseModel):
    """Роль - просмотр."""

    id: uuid.UUID
    name: str

    permissions: Optional[List[PermissionViewSchema]] = None


class PermissionUserSchema(BaseModel):
    """Пермишен пользователя."""

    can_view: bool = False
    can_edit: bool = False
    can_delete: bool = False
    section: SectionViewSchema


class RoleUserPatchSchema(BaseModel):
    """Добавить или убрать роль пользователя."""

    name: str
    delete: bool


class LoginHistorySchema(BaseModel):
    """История логинов."""

    id: uuid.UUID
    user_agent: str
    host: str
    created_at: datetime


class CheckRoleResponse(BaseModel):
    """Проверка роли."""

    name: str
    has: bool


class RoleSimpleSchema(BaseModel):
    """Схема для реквеста."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


class UserRoleSchema(BaseModel):
    """Схема для реквеста."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str

    roles: Optional[List[RoleSimpleSchema]] = None


class UserRoleEnum(str, Enum):
    """Енам ролей."""

    admin = "admin"
