"""Сервисы пользователей."""
import operator
import uuid
from functools import lru_cache
from http import HTTPStatus

from fastapi import Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio.session import AsyncSession
from werkzeug.security import generate_password_hash

from crud.login_history import DBLoginHistory
from crud.permissions import DBPermission
from crud.roles import DBRole
from crud.sections import DBSection
from crud.users import DBUser
from db.postgres import get_db
from db.redis import get_redis
from exceptions.users import UserNotFound
from models.entity import LoginHistory, Permission, Role, Section, User
from schemas.entity import PermissionUserSchema, RoleUserPatchSchema, SectionViewSchema, UserCreate, UserPatchSchema
from services.base import AbstractService


class UserService(AbstractService):
    """Пользовательский сервис."""

    async def register_user(self, user: UserCreate):
        """Сервис регистрации пользователей."""
        user_instance = await DBUser.get_by_field_name(
            db=self.db, _select=User, field_name=User.login, field_value=user.login
        )
        if user_instance:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Login already exists")
        return await DBUser.create(db=self.db, obj_in=user)

    async def patch_user(self, user: UserPatchSchema, current_user: User):
        """Патч логина и пароля."""
        user_instance = await DBUser.get_by_field_name(
            db=self.db, _select=User, field_name=User.login, field_value=user.login
        )
        if user_instance and current_user != user_instance:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Логин уже существует")
        user.password = generate_password_hash(user.password)
        return await DBUser.update(db_obj=current_user, db=self.db, obj_in=user)

    async def check_role(self, role_name: str, user: User):
        """Проверка роли."""
        return {"name": role_name, "has": await DBUser.is_role(role_name=role_name, _uuid=user.id, db=self.db)}

    async def edit_users_role(self, payload: RoleUserPatchSchema, user: User):
        """Назначение и удаление роли пользователя."""
        role = await DBRole.get_by_field_name(field_name=Role.name, field_value=payload.name, db=self.db, _select=Role)
        if not role:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Role not found")

        if payload.delete:
            if not await DBUser.is_role(db=self.db, role_name=payload.name, _uuid=user.id):
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User has no such role")
            await DBUser.remove_role(db=self.db, role=role, user=user)
        else:
            if await DBUser.is_role(db=self.db, role_name=payload.name, _uuid=user.id):
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User already has such role")
            await DBUser.add_role(db=self.db, role=role, user=user)

    async def check_permission(self, section_name: str, user: User) -> PermissionUserSchema:
        """Проверка пермишена."""
        section = await DBSection.get_by_field_name(
            db=self.db, field_name=Section.name, field_value=section_name, _select=Section
        )
        if not section:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Section not found")
        role_ids = [el.id for el in list(user.roles)]
        if not role_ids:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Roles not found")
        permissions = await DBPermission.get_list(
            db=self.db,
            _select=Permission,
            conditions=[(Permission.section_id, section.id, operator.eq)],
            condition_any=[{Permission.role_id: role_ids}],
        )
        if not permissions:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Permissions not found")
        section_schema = SectionViewSchema(**section.__dict__)
        permission_schema = PermissionUserSchema(section=section_schema)
        for el in permissions:
            if el.can_view:
                permission_schema.can_view = True
            if el.can_edit:
                permission_schema.can_edit = True
            if el.can_delete:
                permission_schema.can_delete = True
        return permission_schema

    async def login_history(self, user: User):
        """Получение истории логинов."""
        return await DBLoginHistory.get_list(
            _select=LoginHistory,
            db=self.db,
            conditions=[(LoginHistory.user_id, user.id, operator.eq)],
            order=LoginHistory.created_at,
        )

    async def get_user_by_id(self, user_id: uuid) -> User:
        """Получение пользователя по id прежде всего через кролика."""
        user = await DBUser.get_by_field_name(
            field_name=User.id, field_value=user_id, db=self.db, _select=User, selection_load_options=[(User.roles,)]
        )
        if not user:
            raise UserNotFound(user_id=user_id)
        return user


@lru_cache()
def get_user_service(db: AsyncSession = Depends(get_db), cache: Redis = Depends(get_redis)) -> UserService:
    """Получить сервис жанров."""
    return UserService(db, cache)
