"""Схемы соц сетей."""
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class SocialAuthorizationLink(BaseModel):
    """Схема линка на авторизацию яндекса."""

    url: Optional[str] = None


class SocialEnum(str, Enum):
    """Енам провайдеров."""

    yandex = "yandex"
