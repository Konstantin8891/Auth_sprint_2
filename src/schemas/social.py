"""Схемы соц сетей."""
from pydantic import BaseModel


class SocialAuthorizationLink(BaseModel):
    """Схема линка на авторизацию яндекса."""

    url: str
