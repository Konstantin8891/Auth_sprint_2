"""Сервис жанров."""

from functools import lru_cache
from typing import Dict, List
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from schemas.genres import GenreShortSchema
from schemas.query_params import PaginationParams
from services.base import RedisElasticService


class GenreService(RedisElasticService):
    """Сервис для работы с жанрами."""

    async def _gen_detail_schema(self, result: Dict):
        genre_detail_dict = dict(result["hits"]["hits"][0]["_source"])
        result = GenreShortSchema(uuid=UUID(genre_detail_dict.get("id")), name=genre_detail_dict.get("name"))
        await self._put_to_cache(data=result.model_dump_json(), key=result.uuid)
        return result

    async def get_all(self, pagination: PaginationParams) -> List[GenreShortSchema]:
        """Получить всех жанров."""
        return await self._get_all_genre_from_elastic(pagination)

    async def _get_all_genre_from_elastic(self, page_params: PaginationParams) -> List[GenreShortSchema]:
        """Получить всех жанров из elasticsearch."""
        try:
            result = await self.db.get_list(model=Genre, page_params=page_params)
            result = result["hits"]["hits"]
        except NotFoundError:
            return []

        return [GenreShortSchema(uuid=el["_source"]["id"], name=el["_source"]["name"]) for el in result]


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    """Получить сервис жанров."""
    return GenreService(redis, elastic)
