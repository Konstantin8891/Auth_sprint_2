"""Сервисы пользователей."""
from functools import lru_cache
from http import HTTPStatus

from fastapi import Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio.session import AsyncSession

from crud.sections import DBSection
from db.postgres import get_db
from db.redis import get_redis
from models.entity import Section, User
from schemas.entity import SectionCreateSchema
from services.base import AbstractService


class SectionService(AbstractService):
    """Сервис разделов портала."""

    async def create_section(self, payload: SectionCreateSchema, user: User) -> Section:
        """Создание раздела."""
        section = await DBSection.get_by_field_name(
            field_name=Section.name, field_value=payload.name, db=self.db, _select=Section
        )
        if section:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Section already exists")
        return await DBSection.create(db=self.db, obj_in=payload)

    async def get_sections(self, user: User):
        """Список разделов."""
        return await DBSection.get_list(db=self.db, _select=Section)


@lru_cache()
def get_section_service(db: AsyncSession = Depends(get_db), cache: Redis = Depends(get_redis)) -> SectionService:
    """Получить сервис жанров."""
    return SectionService(db, cache)
