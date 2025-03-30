"""Пользовательский сервис."""

import uuid

import jwt
from fastapi import HTTPException, Request
from jose.exceptions import ExpiredSignatureError

from core.settings import settings


class UserService:
    """Пользовательский сервис."""

    @staticmethod
    async def parse_token(request: Request) -> uuid.UUID:
        """Достаём id из токена."""
        try:
            token = request.headers["authorization"].split(" ")[1]
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            id = payload.get("sub")
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Истек срок действия токена")
        except Exception:
            raise HTTPException(status_code=401, detail="Некорретный токен")
        return id
