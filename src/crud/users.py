"""Пользователи - круд."""

import uuid
from typing import Optional

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio.session import AsyncSession

from crud.base_crud import CRUDSQLAlchemy
from models.entity import Role, User


class CRUDUser(CRUDSQLAlchemy):
    """Круд пользователь."""

    async def is_role(self, db: AsyncSession, *, role_name: str, _uuid: uuid.UUID) -> Optional[User]:
        """Имеет ли пользователь роль."""
        exists_qr = select(User).join(Role, User.roles).where((User.id == _uuid) & (Role.name == role_name))  # noqa
        result = await db.execute(exists(exists_qr).select())
        role_exists = result.scalar()
        return role_exists

    async def is_admin(self, db: AsyncSession, *, _uuid: uuid.UUID) -> User:
        """Является ли пользовтаель админом."""
        role_exists = await self.is_role(db=db, role_name="admin", _uuid=_uuid)
        return role_exists

    @staticmethod
    async def add_role(db: AsyncSession, role: Role, user: User):
        """Назначить роль."""
        user.roles.append(role)
        await db.commit()

    @staticmethod
    async def remove_role(db: AsyncSession, role: Role, user: User):
        """Убрать роль."""
        user.roles.remove(role)
        await db.commit()


DBUser = CRUDUser(User)
