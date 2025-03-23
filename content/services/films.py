"""Сервисы фильмов."""

import json
import logging
import uuid
from functools import lru_cache
from typing import Dict, List, Tuple

from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Q
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.movies import FilmWork
from schemas.films import FilmWorkFullSchema, FilmWorkShortSchema, QueryType
from schemas.genres import GenreShortSchema
from schemas.persons import FilmInPersonSchema, PersonShortSchema, Role
from schemas.query_params import FilmWorkFilterParams, FilmWorkSearchParams, PaginationParams, SortParams
from services.base import RedisElasticService

logger = logging.getLogger(__name__)


class FilmService(RedisElasticService):
    """Сервис фильмов."""

    async def _gen_detail_schema(self, result: Dict) -> FilmWorkFullSchema:
        film_detail_dict = dict(result["hits"]["hits"][0]["_source"])
        _uuid = film_detail_dict.pop("id")
        film_detail_dict["uuid"] = _uuid
        genres_schemas = []
        genres = film_detail_dict.pop("genres", [])
        for i in range(len(genres)):
            _uuid = genres[i]["id"]
            genres[i]["uuid"] = _uuid
            genres_schemas.append(GenreShortSchema(**genres[i]))
        actors_schemas = []
        actors = film_detail_dict.pop("actors", [])
        for i in range(len(actors)):
            _uuid = actors[i]["id"]
            actors[i]["uuid"] = _uuid
            actors_schemas.append(PersonShortSchema(uuid=actors[i]["id"], full_name=actors[i]["name"]))
        writers_schemas = []
        writers = film_detail_dict.pop("writers", [])
        for i in range(len(writers)):
            _uuid = writers[i]["id"]
            writers[i]["uuid"] = _uuid
            writers_schemas.append(PersonShortSchema(uuid=writers[i]["id"], full_name=writers[i]["name"]))
        directors_schemas = []
        directors = film_detail_dict.pop("directors", [])
        for i in range(len(directors)):
            _uuid = directors[i]["id"]
            directors[i]["uuid"] = _uuid
            directors_schemas.append(PersonShortSchema(uuid=directors[i]["id"], full_name=directors[i]["name"]))

        result = FilmWorkFullSchema(
            genres=genres_schemas,
            actors=actors_schemas,
            writers=writers_schemas,
            directors=directors_schemas,
            **film_detail_dict,
        )
        return result

    @staticmethod
    async def _gen_short_film_answer_from_redis(result: bytes) -> List[FilmWorkShortSchema]:
        """Генерация результата из ответа редиса."""
        return [FilmWorkShortSchema(**film) for film in json.loads(result)]

    @staticmethod
    async def _gen_short_film_answer_from_elastic(result: Dict) -> Tuple[List[FilmWorkShortSchema], List[Dict]]:
        """Генерация результата из ответа эластика."""
        schemas = []
        schemas_json = []
        for el in result["hits"]["hits"]:
            film = FilmWorkShortSchema(
                uuid=el["_source"]["id"],
                title=el["_source"]["title"],
                imdb_rating=el["_source"]["imdb_rating"],
            )
            schemas.append(film)
            schemas_json.append(film.model_dump(mode="json"))
        return schemas, schemas_json

    async def get_films(
        self,
        sort_params: SortParams,
        page_params: PaginationParams,
        filter_params: FilmWorkFilterParams,
    ) -> List[FilmWorkShortSchema]:
        """Получить список популярных фильмов."""
        key = f"get_films-page_size-{page_params.page_size}_page-{page_params.page}"
        if filter_params.genre_id:
            key += f"genre_id={filter_params.genre_id}"
            result = await self._get_from_cache(key=key)
            if result:
                return await self._gen_short_film_answer_from_redis(result=result)
            nested_query = Q(QueryType.multi_match.name, query=filter_params.genre_id, fields=["genres.id"])
            result = await self.db.get_list(
                model=FilmWork,
                query_type=QueryType.nested.name,
                path="genres",
                query=nested_query,
                page_params=page_params,
                sort=sort_params.sort,
            )
        else:
            result = await self._get_from_cache(key=key)
            if result:
                return await self._gen_short_film_answer_from_redis(result=result)
            result = await self.db.get_list(model=FilmWork, sort="-imdb_rating", page_params=page_params)
        result, schemas_json = await self._gen_short_film_answer_from_elastic(result=result)
        await self._put_to_cache(key=key, data=json.dumps(schemas_json))
        return result

    async def search(
        self,
        page_params: PaginationParams,
        search_params: FilmWorkSearchParams,
    ) -> List[FilmWorkShortSchema]:
        """Поиск фильмов по названию."""
        key = f"search_films-page_size-{page_params.page_size}_page-{page_params.page}_query-{search_params.query}"
        result = await self._get_from_cache(key=key)
        if result:
            return [FilmWorkShortSchema(**film) for film in json.loads(result)]
        result = await self.db.get_list(
            model=FilmWork,
            query_type=QueryType.multi_match.name,
            query=search_params.query,
            fields=["title"],
            sort="-imdb_rating",
            page_params=page_params,
        )
        result, schemas_json = await self._gen_short_film_answer_from_elastic(result=result)
        await self._put_to_cache(key=key, data=json.dumps(schemas_json))
        return result

    async def _gen_films_by_person_response(
        self, result: Dict, person_id: uuid.UUID
    ) -> Tuple[List[FilmInPersonSchema], List[Dict]]:
        film_list = []
        film_list_json = []
        for el in result["hits"]["hits"]:
            roles = []
            for actor in el["_source"]["actors"]:
                if actor["id"] == person_id:
                    roles.append(Role.actor)
                    break
            for director in el["_source"]["directors"]:
                if director["id"] == person_id:
                    roles.append(Role.director)
                    break
            for writer in el["_source"]["writers"]:
                if writer["id"] == person_id:
                    roles.append(Role.writer)
                    break

            film = FilmInPersonSchema(
                uuid=el["_source"]["id"],
                roles=roles,
            )
            film_list.append(film)
            film_list_json.append(film.model_dump(mode="json"))
        return film_list, film_list_json

    async def get_films_by_person(
        self,
        person_id: uuid.UUID,
    ) -> List[FilmInPersonSchema]:
        """Поиск фильма по персоне. Так как гуиды условно уникальные, предалагаю использовать простой мульти матч."""
        person_id = str(person_id)
        key = f"films_by_person-{person_id}"
        film_list = await self._get_from_cache(key=key)
        if film_list:
            film_list_cache = json.loads(film_list)
            film_list = []
            for person in film_list_cache:
                film_list.append(FilmInPersonSchema(**person))
            return film_list
        nested_actors_query = Q(QueryType.multi_match.name, query=person_id, fields=["actors.id"])
        nested_directors_query = Q(QueryType.multi_match.name, query=person_id, fields=["directors.id"])
        nested_writers_query = Q(QueryType.multi_match.name, query=person_id, fields=["writers.id"])
        query = (
            Q(QueryType.nested.name, query=nested_actors_query, path="actors")
            | Q(QueryType.nested.name, query=nested_directors_query, path="directors")
            | Q(QueryType.nested.name, query=nested_writers_query, path="writers")
        )
        result = await self.db.get_list(
            model=FilmWork,
            multiple_queries=True,
            query=query,
            sort="-imdb_rating",
        )

        film_list, film_list_json = await self._gen_films_by_person_response(result=result, person_id=person_id)
        await self._put_to_cache(key=key, data=json.dumps(film_list_json))
        return film_list


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    """Получить сервис жанров."""
    return FilmService(redis, elastic)
