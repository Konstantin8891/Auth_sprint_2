"""Сервисы авторизации."""
import logging
import operator
from functools import lru_cache
from http import HTTPStatus
from typing import List

import httpx
from fastapi import Depends, HTTPException, Request
from jose import JWTError, jwt
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio.session import AsyncSession

from core.config import settings
from crud.login_history import DBLoginHistory
from crud.roles import DBRole
from crud.users import DBUser
from db.postgres import get_db
from db.redis import get_redis
from models.entity import LoginHistory, Role, User
from schemas.entity import RefreshSchema, TokenSchema, UserLoginSchema
from schemas.social import SocialAuthorizationLink
from services.base import AbstractService
from utils.auth import create_access_token, create_refresh_token

logger = logging.getLogger(__name__)


class AuthService(AbstractService):
    """Сервис авторизации."""

    @staticmethod
    async def get_id_from_token(request: Request) -> str:
        """Получение первичного ключа из токена."""
        token = request.headers["authorization"].split(" ")[1]
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload.get("sub")

    @staticmethod
    async def get_nested_key(login_history: LoginHistory) -> str:
        """Формирование ключа вложенной хеш структуры."""
        return login_history.user_agent + login_history.host + str(login_history.user_id)

    async def hget_from_cache(self, user_id: str, nested_key: str) -> str:
        """Получение значений из хеш структуры."""
        return await self.cache.hget(name=user_id, key=nested_key)

    async def hset_to_cache(
        self, user_id: str, nested_key: str, refresh_token: str, nx: bool, xx: bool, gt: bool, lt: bool
    ) -> None:
        """Запись значений в хеш структуру."""
        await self.cache.hset(name=user_id, mapping={nested_key: refresh_token})
        await self.cache.hexpire(
            user_id, settings.refresh_token_expire_minutes * 60, nested_key, nx=nx, xx=xx, gt=gt, lt=lt
        )

    async def hdel(self, user_id: str, keys: List[str]) -> None:
        """Удаление ключей хеш структуры."""
        await self.cache.hdel(user_id, *keys)

    async def login(self, payload: UserLoginSchema, request: Request) -> TokenSchema:
        """Логин."""
        user = await DBUser.get_by_field_name(
            db=self.db,
            _select=User,
            field_name=User.login,
            field_value=payload.login,
            selection_load_options=[(User.roles,)],
        )
        if not user:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Неверный логин или пароль")
        if not user.check_password(payload.password):
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Неверный логин или пароль")
        login_history = await DBLoginHistory.create(
            db=self.db,
            obj_in={
                "user_id": user.id,
                "user_agent": request.headers.get("user-agent"),
                "host": request.headers.get("host"),
            },
        )
        role_ids = [str(el.id) for el in user.roles]
        access_token = create_access_token(subject=user.id, role_ids=role_ids)
        refresh_token = create_refresh_token(subject=user.id)
        nested_key = await self.get_nested_key(login_history)
        await self.hset_to_cache(
            user_id=str(user.id),
            nested_key=nested_key,
            refresh_token=refresh_token,
            nx=True,
            xx=False,
            gt=False,
            lt=False,
        )

        return TokenSchema(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh(self, payload: RefreshSchema, request: Request) -> TokenSchema:
        """Рефреш."""
        try:
            payload_token = jwt.decode(payload.refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        except JWTError:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Ошибка авторизации")
        user = await DBUser.get_by_field_name(
            db=self.db,
            field_value=payload_token.get("sub"),
            field_name=User.id,
            _select=User,
        )
        login_history = await DBLoginHistory.create(
            db=self.db,
            obj_in={
                "user_id": user.id,
                "user_agent": request.headers.get("user-agent"),
                "host": request.headers.get("host"),
            },
        )

        nested_key = await self.get_nested_key(login_history)

        old_token = await self.hget_from_cache(user_id=str(user.id), nested_key=nested_key)
        if not old_token or old_token.decode() != payload.refresh_token:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Ошибка вайтлиста токенов")

        access_token = create_access_token(subject=user.id, role_ids=[1])
        refresh_token = create_refresh_token(subject=user.id)

        await self.hset_to_cache(
            user_id=str(user.id),
            nested_key=nested_key,
            refresh_token=refresh_token,
            nx=False,
            xx=True,
            gt=False,
            lt=False,
        )

        # Роли пока заглушка
        return TokenSchema(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def logout(self, request: Request, current_user: User):
        """Логаут."""
        _id = await self.get_id_from_token(request=request)
        user = await DBUser.get_by_field_name(db=self.db, field_name=User.id, field_value=_id, _select=User)
        login_history = await DBLoginHistory.get_by_field_name(
            db=self.db,
            _select=LoginHistory,
            field_name=LoginHistory.user_agent,
            field_value=request.headers.get("user-agent"),
            conditions=[(LoginHistory.host, request.headers.get("host"), operator.eq)],
        )
        if login_history:
            nested_key = await self.get_nested_key(login_history)

            refresh_token = await self.hget_from_cache(user_id=str(current_user.id), nested_key=nested_key)

            if refresh_token:
                await self.hdel(str(user.id), [nested_key])

    async def logout_all(self, request: Request, current_user: User):
        """Выйти из всех устройств."""
        _id = await self.get_id_from_token(request=request)
        user = await DBUser.get_by_field_name(db=self.db, field_name=User.id, field_value=_id, _select=User)
        login_history = await DBLoginHistory.get_by_field_name(
            db=self.db,
            _select=LoginHistory,
            field_name=LoginHistory.user_agent,
            field_value=request.headers.get("user-agent"),
            conditions=[(LoginHistory.host, request.headers.get("host"), operator.eq)],
        )
        if login_history:
            keys = await self.cache.hgetall(str(user.id))
            if keys:
                await self.hdel(str(user.id), list(keys.keys()))


@lru_cache()
def get_auth_service(db: AsyncSession = Depends(get_db), cache: Redis = Depends(get_redis)) -> AuthService:
    """Получить сервис жанров."""
    return AuthService(db, cache)


class SocialService(AbstractService):
    """Сервис авторизации через сторонние приложения."""

    def __init__(self, db: AsyncSession, cache: Redis) -> None:
        """Инициализация сервиса."""
        self.auth_service = get_auth_service(db, cache)
        super().__init__(db, cache)

    @staticmethod
    async def get_link() -> SocialAuthorizationLink:
        """Линк авторизации в яндексе."""
        return SocialAuthorizationLink(
            url=(settings.yandex_oauth_authorize + "?response_type=code&client_id=" + settings.yandex_client_id)
        )

    async def get_tokens(self, code: str):
        """Возвращает токены по коду яндекса."""
        params = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": settings.yandex_client_id,
            "client_secret": settings.yandex_client_secret,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=settings.yandex_oauth_token,
                data=params,
                params=params,
                headers={"content-type": "application/x-www-form-urlencoded"},
            )
        access_token = response.json().get("access_token")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=settings.yandex_oauth_profile,
                params={"format": "json"},
                headers={"Authorization": f"OAuth {access_token}"},
            )

        response = response.json()

        login = response.get("login")
        first_name = response.get("first_name")
        last_name = response.get("last_name")

        user = await DBUser.get_by_field_name(
            db=self.db, _select=User, field_name=User.login, field_value=login, selection_load_options=[(User.roles,)]
        )
        if user:
            logger.info("User logged in from yandex")
            logger.info(user)
            role_ids = [str(el.id) for el in user.roles]
        else:
            await DBUser.create(db=self.db, obj_in={"login": login, "first_name": first_name, "last_name": last_name})
            user = await DBUser.get_by_field_name(
                db=self.db,
                _select=User,
                field_name=User.login,
                field_value=login,
                selection_load_options=[(User.roles,)],
            )
            role = await DBRole.get_by_field_name(db=self.db, _select=Role, field_name=Role.name, field_value="user")
            await DBUser.add_role(db=self.db, role=role, user=user)
            logger.info("User created from yandex")
            logger.info(user)
            role_ids = [role.id]
        login_history = await DBLoginHistory.create(
            db=self.db,
            obj_in={
                "user_id": user.id,
                "user_agent": "yandex",
                "host": "https://ya.ru",
            },
        )
        nested_key = await self.auth_service.get_nested_key(login_history)
        access_token = create_access_token(subject=user.id, role_ids=role_ids)
        refresh_token = create_refresh_token(subject=user.id)
        await self.auth_service.hset_to_cache(
            user_id=str(user.id),
            nested_key=nested_key,
            refresh_token=refresh_token,
            nx=True,
            xx=False,
            gt=False,
            lt=False,
        )
        return {"access_token": access_token, "refresh_token": refresh_token}


@lru_cache()
def get_social_service(db: AsyncSession = Depends(get_db), cache: Redis = Depends(get_redis)) -> SocialService:
    """Получить сервис жанров."""
    return SocialService(db, cache)
