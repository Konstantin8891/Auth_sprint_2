"""Ручки auth."""
from http import HTTPStatus

from fastapi import APIRouter, Depends, Request

from models.entity import User
from schemas.entity import RefreshSchema, TokenSchema, UserCreate, UserInDB, UserLoginSchema
from schemas.social import SocialAuthorizationLink
from services.auth import AuthService, SocialService, get_auth_service, get_social_service
from services.users import UserService, get_user_service
from utils.auth import get_current_user

router = APIRouter()


@router.post("/signup", summary="Register user", response_model=UserInDB, status_code=HTTPStatus.CREATED)
async def create_user(user_create: UserCreate, user_service: UserService = Depends(get_user_service)) -> UserInDB:
    """Регистрация."""
    return await user_service.register_user(user=user_create)


@router.post("/login", summary="Get token", response_model=TokenSchema)
async def login(
    request: Request, user: UserLoginSchema, auth_service: AuthService = Depends(get_auth_service)
) -> TokenSchema:
    """Логин."""
    return await auth_service.login(payload=user, request=request)


@router.post("/refresh", summary="Refresh token", response_model=TokenSchema)
async def refresh(
    request: Request, user: RefreshSchema, auth_service: AuthService = Depends(get_auth_service)
) -> TokenSchema:
    """Рефреш."""
    return await auth_service.refresh(payload=user, request=request)


@router.delete("/logout", summary="Logout", response_model=None)
async def logout(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
):
    """Логаут."""
    return await auth_service.logout(request=request, current_user=current_user)


@router.delete("/logout/all", summary="Logout on all devices", response_model=None)
async def logout_all(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
):
    """Выйти из всех устройств."""
    return await auth_service.logout_all(request=request, current_user=current_user)


@router.get("/social", summary="Return authorization link", response_model=SocialAuthorizationLink)
async def get_social_link(social_service: SocialService = Depends(get_social_service)) -> SocialAuthorizationLink:
    """Получение ссылки аваторизации в Яндексе."""
    return await social_service.get_link()


@router.get("/social/yandex_auth", summary="Get token by yandex login", response_model=None)
async def get_tokens(code: str, social_service: SocialService = Depends(get_social_service)) -> None:
    """Получение токенов авторизации на беке по коду."""
    return await social_service.get_tokens(code=code)
