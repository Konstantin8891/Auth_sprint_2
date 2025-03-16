"""Корневой роутер."""

from fastapi import APIRouter, Depends

from utils.auth import get_current_user_global

from .v1.auth import router as v1_auth_router
from .v1.roles import router as v1_roles_router
from .v1.sections import router as v1_section_router
from .v1.users import router as v1_users_router

router = APIRouter()

router.include_router(v1_auth_router, tags=["Auth"], prefix="/v1/auth")
router.include_router(
    v1_roles_router, tags=["Roles"], prefix="/v1/roles", dependencies=[Depends(get_current_user_global)]
)
router.include_router(
    v1_section_router, tags=["Sections"], prefix="/v1/sections", dependencies=[Depends(get_current_user_global)]
)
router.include_router(v1_users_router, tags=["Users"], prefix="/v1/users")
