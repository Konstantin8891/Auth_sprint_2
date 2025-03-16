"""Пользователи."""

from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate

from models.entity import User
from schemas.entity import LoginHistorySchema, UserInDB, UserPatchSchema
from services.users import UserService, get_user_service
from utils.auth import get_current_user

router = APIRouter()


@router.patch("", summary="Patch user", response_model=UserInDB)
async def patch_user(
    user_patch: UserPatchSchema,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Патч логина и пароля."""
    return await user_service.patch_user(user=user_patch, current_user=current_user)


@router.get("/login_history", summary="Login history", response_model=Page[LoginHistorySchema])
async def login_history(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> Page[LoginHistorySchema]:
    """История логинов."""
    result = await user_service.login_history(user=current_user)
    return paginate(result)
