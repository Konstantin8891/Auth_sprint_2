"""Утилиты модуля auth."""
import logging
from datetime import UTC, datetime, timedelta
from typing import Any, List, Union

from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from core.config import settings

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.login_url)


def create_access_token(subject: Union[str, Any], role_ids: List, expires_delta: int = None) -> str:
    """Аксесс токен."""
    if expires_delta is not None:
        expires_delta = datetime.now(UTC) + expires_delta
    else:
        expires_delta = datetime.now(UTC) + timedelta(minutes=int(settings.access_token_expire_minutes))

    to_encode = {
        "exp": expires_delta,
        "sub": str(subject),
        "type": "access",
        "roles": role_ids,
    }
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, settings.algorithm)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    """Рефреш токен."""
    if expires_delta is not None:
        expires_delta = datetime.now(UTC) + expires_delta
    else:
        expires_delta = datetime.now(UTC) + timedelta(minutes=settings.refresh_token_expire_minutes)

    to_encode = {"exp": expires_delta, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, settings.algorithm)
    return encoded_jwt
