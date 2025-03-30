"""Сервисы пользователей."""

import uuid
from functools import lru_cache

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession

from crud.users import DBUser
from db.postgres import get_db
from models.entity import User
from services.base import AbstractService


class UserService(AbstractService):
    """Пользовательский сервис."""

    async def get_user_by_id(self, user_id: uuid) -> User:
        """Получение пользователя по id провалилось (кроме 404) возвращаем дефолтного пользователя."""
        user = await DBUser.get_by_field_name(
            field_name=User.login,
            field_value="default_user",
            db=self.db,
            _select=User,
            selection_load_options=[(User.roles,)],
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user


@lru_cache()
def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Получить сервис жанров."""
    return UserService(db)
