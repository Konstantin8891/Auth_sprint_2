"""Ручки auth."""
from fastapi import APIRouter, Depends

from schemas.entity import TokenSchema, UserLoginSchema
from services.auth import AuthService, get_auth_service

router = APIRouter()


@router.post("/login", summary="Get token", response_model=TokenSchema)
async def login(user: UserLoginSchema, auth_service: AuthService = Depends(get_auth_service)) -> TokenSchema:
    """Логин."""
    return await auth_service.login(payload=user)
