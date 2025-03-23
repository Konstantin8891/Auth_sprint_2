"""Корневой роутер."""

from fastapi import APIRouter

from .v1.auth import router as v1_auth_router

router = APIRouter()

router.include_router(v1_auth_router, tags=["Auth"], prefix="/v1/auth")
