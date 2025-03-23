"""Базовый класс для всех сервисов."""

import json
import uuid
from abc import ABC, abstractmethod
from http import HTTPStatus
from typing import Any, Dict, Union

from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import AsyncDocument
from fastapi import HTTPException
from pydantic import BaseModel
from redis.asyncio import Redis

from core.settings import settings
from db.elastic import ElasticCRUD


class AbstractService(ABC):
    """Абстрактный сервис."""

    def __init__(self, cache: Any, db: Any):
        """Инициализация сервиса."""
        self.cache = cache
        self.db = ElasticCRUD(db)
        self.cache_expire_in_seconds = settings.cache_expire_in_seconds

    @abstractmethod
    async def _get_from_cache(self, key: Any) -> Any:
        """Получение кеша."""
        pass

    @abstractmethod
    async def _put_to_cache(self, data: str, key: Any) -> Any:
        """Запись в кеш."""
        pass

    @abstractmethod
    async def get_by_id(self, _id, model: Any, schema: Any) -> Any:
        """Получение по id."""
        pass

    @abstractmethod
    async def _gen_detail_schema(self, result: Dict) -> Any:
        """Генерация ответа деталки из ответа базы данных."""
        pass


class RedisElasticService(AbstractService):
    """Сервис редиса и эластика."""

    def __init__(self, cache: Redis, db: AsyncElasticsearch):
        """Инициализация сервиса."""
        super().__init__(cache, db)
        self.cache = cache
        self.db = ElasticCRUD(db)
        self.cache_expire_in_seconds = settings.cache_expire_in_seconds

    async def _get_from_cache(self, key: Union[uuid.UUID, str]) -> bytes | None:
        """Получить объект по id из кэша."""
        data = await self.cache.get(str(key))
        if not data:
            return None
        return data

    async def _put_to_cache(self, data: str, key: Union[str, uuid.UUID]) -> None:
        """Записать объект в кэш."""
        await self.cache.set(str(key), data, self.cache_expire_in_seconds)

    async def _gen_detail_schema(self, result: Dict) -> Any:
        """Валидация ответа (деталка) от эластика."""
        return result

    async def get_by_id(self, _id: uuid.UUID, model: AsyncDocument, schema: type[BaseModel]) -> Any:
        """Деталка фильма."""
        result = await self._get_from_cache(key=_id)
        if result:
            return schema(**json.loads(result))
        result = await self.db.get_detail(model=model, _id=_id)
        if result:
            result = await self._gen_detail_schema(result)
            await self._put_to_cache(data=result.model_dump_json(), key=result.uuid)
            return result
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Объект не найден")
