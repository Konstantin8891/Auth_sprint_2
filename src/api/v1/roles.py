"""Роли."""

import uuid
from typing import List

from fastapi import APIRouter, Depends

from models.entity import User
from schemas.entity import (
    CheckRoleResponse,
    PermissionUserSchema,
    RoleCreateSchema,
    RoleUserPatchSchema,
    RoleViewSchema,
    UserRoleEnum,
)
from services.roles import RoleService, get_role_service
from services.users import UserService, get_user_service
from utils.auth import AuthRequest, get_current_user, roles_required

router = APIRouter()


@router.post("", summary="Add role", response_model=RoleViewSchema)
@roles_required(roles_list=[UserRoleEnum.admin])
async def create_role(
    payload: RoleCreateSchema,
    request: AuthRequest,
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
) -> RoleViewSchema:
    """Создание роли."""
    return await role_service.create_role(payload=payload, user=current_user)


@router.get("", summary="Get roles", response_model=List[RoleViewSchema])
@roles_required(roles_list=[UserRoleEnum.admin])
async def get_roles(
    request: AuthRequest,
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
) -> List[RoleViewSchema]:
    """Список ролей."""
    return await role_service.get_roles(user=current_user)


@router.get("/user", summary="Check role", response_model=CheckRoleResponse)
@roles_required(roles_list=[UserRoleEnum.admin])
async def check_role(
    role_name: str,
    request: AuthRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> CheckRoleResponse:
    """Проверка роли."""
    return await user_service.check_role(user=current_user, role_name=role_name)


@router.patch("/user", summary="Add or delete role of user", response_model=None)
@roles_required(roles_list=[UserRoleEnum.admin])
async def patch_users_role(
    request: AuthRequest,
    payload: RoleUserPatchSchema,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> None:
    """Назначить/убрать роль пользователю."""
    return await user_service.edit_users_role(user=current_user, payload=payload)


@router.get("/permissions", summary="Check permission", response_model=PermissionUserSchema)
async def check_permission(
    section_name: str,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> PermissionUserSchema:
    """Проверка пермишена."""
    return await user_service.check_permission(user=current_user, section_name=section_name)


@router.get("/{role_id}", summary="Get role", response_model=RoleViewSchema)
@roles_required(roles_list=[UserRoleEnum.admin])
async def get_role(
    request: AuthRequest,
    role_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
) -> RoleViewSchema:
    """Получение роли."""
    return await role_service.get_role(user=current_user, role_id=role_id)


@router.patch("/{role_id}", summary="Put role", response_model=RoleViewSchema)
@roles_required(roles_list=[UserRoleEnum.admin])
async def patch_role(
    request: AuthRequest,
    role_id: uuid.UUID,
    payload: RoleCreateSchema,
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
) -> RoleViewSchema:
    """Обновление роли."""
    return await role_service.patch_role(user=current_user, role_id=role_id, payload=payload)


@router.delete("/{role_id}", summary="Delete role", response_model=None, status_code=204)
@roles_required(roles_list=[UserRoleEnum.admin])
async def delete_role(
    request: AuthRequest,
    role_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
) -> None:
    """Удаление роли."""
    return await role_service.delete_role(user=current_user, role_id=role_id)
