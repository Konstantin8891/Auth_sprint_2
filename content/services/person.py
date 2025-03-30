"""Сервис персон."""

import json
import logging
from functools import lru_cache
from typing import Dict, List, Tuple
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import AsyncDocument
from fastapi import Depends
from pydantic import BaseModel
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import PersonShort
from schemas.films import QueryType
from schemas.persons import PersonFullSchema, PersonShortSchema
from schemas.query_params import PaginationParams, PersonSearchParams
from services.base import RedisElasticService
from services.films import FilmService

logger = logging.getLogger(__name__)


class PersonService(RedisElasticService):
    """Сервис для работы с персонами."""

    def __init__(self, cache: Redis, db: AsyncElasticsearch):
        """Инит."""
        super().__init__(cache, db)
        self.film_service = FilmService(cache, db)

    async def _gen_detail_schema(self, result: Dict):
        """Генерация ответа деталки из ответа эластика."""
        person_detail_dict = dict(result["hits"]["hits"][0]["_source"])
        result = PersonShortSchema(uuid=UUID(person_detail_dict.pop("id")), **person_detail_dict)
        await self._put_to_cache(key=result.uuid, data=result.model_dump_json())
        return result

    async def get_by_id(self, _id: UUID, model: AsyncDocument, schema: type[BaseModel]) -> PersonFullSchema | None:
        """Получить персоны по его id."""
        person = await super().get_by_id(_id, model, schema)
        film_service = FilmService(self.cache, self.db)
        films = await film_service.get_films_by_person(_id)
        person_full = PersonFullSchema(**person.model_dump(), films=films)
        return person_full

    async def _gen_search_answer(self, result: Dict) -> Tuple[List[PersonFullSchema], List[Dict]]:
        person_list = []
        person_list_json = []
        for el in result["hits"]["hits"]:
            person = PersonShortSchema(
                uuid=el["_source"]["id"],
                full_name=el["_source"]["full_name"],
            )
            films = await self.film_service.get_films_by_person(person.uuid)
            person_list.append(PersonFullSchema(**person.model_dump(), films=films))
            person_list_json.append(person.model_dump(mode="json"))
        return person_list, person_list_json

    async def search(self, search_params: PersonSearchParams, pagination: PaginationParams) -> List[PersonFullSchema]:
        """Получить всех жанров."""
        key = f"search_person-page_size-{pagination.page_size}_page-{pagination.page}_query-{search_params.query}"
        person_list = await self._get_from_cache(key)
        if person_list:
            person_list_cache = json.loads(person_list)
            person_list = []
            for person in person_list_cache:
                person = PersonShortSchema(**person)
                films = await self.film_service.get_films_by_person(person.uuid)
                person_list.append(PersonFullSchema(**person.model_dump(), films=films))
            return person_list
        result = await self.db.get_list(
            model=PersonShort,
            query_type=QueryType.multi_match.name,
            query=search_params.query,
            fields=("full_name",),
            page_params=pagination,
        )
        person_list, person_list_json = await self._gen_search_answer(result)
        await self._put_to_cache(key=key, data=json.dumps(person_list_json))
        return person_list


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    """Получить сервис жанров."""
    return PersonService(redis, elastic)
