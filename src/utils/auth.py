"""Утилиты модуля auth."""
import logging
from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Annotated, Any, List, Union

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.ext.asyncio.session import AsyncSession

from core.config import settings
from crud.users import DBUser
from db.postgres import get_db
from models.entity import User
from schemas.entity import UserRoleEnum, UserRoleSchema

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


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)):
    """Получение пользователя из токена."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Ошибка валидации токена",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    user = await DBUser.get_by_field_name(
        db=db, field_value=username, field_name=User.id, _select=User, selection_load_options=[(User.roles,)]
    )
    if user is None:
        raise credentials_exception
    return user


class AuthRequest(Request):
    """Прокидывание модели пользователя в реквест."""

    custom_user: UserRoleSchema


class JWTBearer(HTTPBearer):
    """Кастомизация Bearer token авторизации."""

    def __init__(self, auto_error: bool = True):
        """Инит."""
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request, db: AsyncSession = Depends(get_db)) -> UserRoleSchema | None:
        """Возврат схемы пользователя."""
        authorize = AuthJWT(req=request)
        authorize._algorithm = settings.algorithm
        authorize._secret_key = settings.secret_key
        await authorize.jwt_optional()
        user_id = await authorize.get_jwt_subject()
        if not user_id:
            return None
        user = await DBUser.get_by_field_name(
            db=db, field_name=User.id, field_value=user_id, _select=User, selection_load_options=[(User.roles,)]
        )
        return UserRoleSchema.model_validate(user)


async def get_current_user_global(request: AuthRequest, user: AsyncSession = Depends(JWTBearer())):
    """Прокидывание пользователя на корневом уровне."""
    request.custom_user = user  # noqa


def roles_required(roles_list: list[UserRoleEnum]):
    """Декоратор роли."""

    def decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            user: UserRoleSchema = kwargs.get("request").custom_user

            if not user:
                raise HTTPException(
                    detail="Unauthorized",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )
            user_roles = [el.name for el in user.roles]
            user_roles = set(user_roles)
            required_roles = [x.value for x in roles_list]
            required_roles = set(required_roles)
            if not required_roles.intersection(user_roles):
                raise HTTPException(
                    detail="Forbidden",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            return await function(*args, **kwargs)

        return wrapper

    return decorator
