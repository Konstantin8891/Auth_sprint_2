"""Разделы."""

from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends

from models.entity import User
from schemas.entity import SectionCreateSchema, SectionViewSchema, UserRoleEnum
from services.sections import SectionService, get_section_service
from utils.auth import AuthRequest, get_current_user, roles_required

router = APIRouter()


@router.post("", summary="Create section", response_model=SectionViewSchema, status_code=HTTPStatus.CREATED)
@roles_required(roles_list=[UserRoleEnum.admin])
async def create_section(
    request: AuthRequest,
    payload: SectionCreateSchema,
    current_user: User = Depends(get_current_user),
    section_service: SectionService = Depends(get_section_service),
) -> SectionViewSchema:
    """Создание раздела."""
    return await section_service.create_section(payload=payload, user=current_user)


@router.get("", summary="Get sections", response_model=List[SectionViewSchema])
@roles_required(roles_list=[UserRoleEnum.admin])
async def get_sections(
    request: AuthRequest,
    current_user: User = Depends(get_current_user),
    section_service: SectionService = Depends(get_section_service),
) -> List[SectionViewSchema]:
    """Получение разделов."""
    return await section_service.get_sections(user=current_user)
