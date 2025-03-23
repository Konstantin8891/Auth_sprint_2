"""Сервисы авторизации."""
import logging
from functools import lru_cache
from http import HTTPStatus

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession

from crud.users import DBUser
from db.postgres import get_db
from models.entity import User
from schemas.entity import TokenSchema, UserLoginSchema
from services.base import AbstractService
from utils.auth import create_access_token, create_refresh_token

logger = logging.getLogger(__name__)


class AuthService(AbstractService):
    """Сервис авторизации."""

    async def login(self, payload: UserLoginSchema) -> TokenSchema:
        """Логин."""
        user = await DBUser.get_by_field_name(
            db=self.db,
            _select=User,
            field_name=User.login,
            field_value="default_user",
            selection_load_options=[(User.roles,)],
        )
        if not user:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Неверный логин или пароль")
        role_ids = [str(el.id) for el in user.roles]
        access_token = create_access_token(subject=user.id, role_ids=role_ids)
        refresh_token = create_refresh_token(subject=user.id)
        return TokenSchema(
            access_token=access_token,
            refresh_token=refresh_token,
        )


@lru_cache()
def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Получить сервис жанров."""
    return AuthService(db)
