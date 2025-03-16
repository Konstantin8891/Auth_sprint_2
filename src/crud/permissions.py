"""Круд пермишен."""

import uuid
from typing import List

from sqlalchemy.ext.asyncio.session import AsyncSession

from crud.base_crud import CRUDSQLAlchemy
from models.entity import Permission


class CRUDPermission(CRUDSQLAlchemy):
    """Круд пермишен."""

    async def bulk_remove(self, db: AsyncSession, ids: List[uuid.UUID]) -> None:
        """Удаление."""
        objs = await self.get_list(db=db, _select=self.model, condition_any=[{self.model.id: ids}])
        for el in objs:
            await db.delete(el)
        await db.commit()


DBPermission = CRUDPermission(Permission)
