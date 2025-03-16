"""Сервисы пользователей."""
import logging
import uuid
from functools import lru_cache
from http import HTTPStatus
from typing import List

from fastapi import Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio.session import AsyncSession

from crud.permissions import DBPermission
from crud.roles import DBRole
from crud.sections import DBSection
from db.postgres import get_db
from db.redis import get_redis
from models.entity import Permission, Role, Section, User
from schemas.entity import RoleCreateSchema
from services.base import AbstractService

logger = logging.getLogger(__name__)


class RoleService(AbstractService):
    """Пользовательский сервис."""

    async def create_role(self, payload: RoleCreateSchema, user: User) -> Role:
        """Создание роли."""
        role = await DBRole.get_by_field_name(field_name=Role.name, field_value=payload.name, db=self.db, _select=Role)
        if role:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Role already exists")
        role = await DBRole.create(db=self.db, obj_in={"name": payload.name})
        for el in payload.permissions:
            el = el.model_dump()
            el["role_id"] = role.id
            await DBPermission.create(db=self.db, obj_in=el)
        return await DBRole.get_by_field_name(
            field_name=Role.id,
            field_value=role.id,
            _select=Role,
            selection_load_options=[(Role.permissions, Permission.section)],
            db=self.db,
        )

    async def get_roles(self, user: User) -> List[Role]:
        """Список ролей."""
        return await DBRole.get_list(
            _select=Role,
            selection_load_options=[(Role.permissions, Permission.section)],
            db=self.db,
        )

    async def get_role(self, user: User, role_id: uuid.UUID) -> Role:
        """Получение роли."""
        role = await DBRole.get_by_field_name(
            field_name=Role.id,
            field_value=role_id,
            _select=Role,
            selection_load_options=[(Role.permissions, Permission.section)],
            db=self.db,
        )
        if not role:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Role not found")
        return role

    async def patch_role(self, user: User, role_id: uuid.UUID, payload: RoleCreateSchema) -> Role:
        """Обновление роли."""
        role = await DBRole.get_by_field_name(
            field_name=Role.id,
            field_value=role_id,
            db=self.db,
            _select=Role,
        )
        if not role:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Role does not exist")
        await DBRole.update(db=self.db, obj_in={"name": payload.name}, db_obj=role)
        role = await DBRole.get_by_field_name(
            field_name=Role.id,
            field_value=role_id,
            db=self.db,
            _select=Role,
            selection_load_options=[(Role.permissions, Permission.section)],
        )
        permission_ids = [el.id for el in list(role.permissions)]
        await DBPermission.bulk_remove(db=self.db, ids=permission_ids)
        for el in payload.permissions:
            section = await DBSection.get_by_field_name(
                db=self.db, _select=Section, field_name=Section.id, field_value=el.section_id
            )
            if not section:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Section not found")
            el = el.model_dump()
            el["role_id"] = role.id
            await DBPermission.create(db=self.db, obj_in=el)
        role = await DBRole.get_by_field_name(
            field_name=Role.id,
            field_value=role.id,
            _select=Role,
            selection_load_options=[(Role.permissions, Permission.section)],
            db=self.db,
        )
        return role

    async def delete_role(self, user: User, role_id: uuid.UUID):
        """Удаление роли."""
        role = await DBRole.get_by_field_name(
            field_name=Role.id,
            field_value=role_id,
            db=self.db,
            _select=Role,
            selection_load_options=[(Role.permissions,)],
        )
        if not role:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Role does not exist")
        permission_ids = [el.id for el in list(role.permissions)]
        if permission_ids:
            await DBPermission.bulk_remove(db=self.db, ids=permission_ids)
        await DBRole.remove(db=self.db, _id=role_id)


@lru_cache()
def get_role_service(db: AsyncSession = Depends(get_db), cache: Redis = Depends(get_redis)) -> RoleService:
    """Получить сервис жанров."""
    return RoleService(db, cache)
