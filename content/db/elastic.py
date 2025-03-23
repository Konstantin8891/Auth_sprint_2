"""Интерфейс доступа к ElasticSearch."""

import logging
import uuid
from enum import Enum
from typing import Any, List, Tuple, Union

from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import AsyncDocument

from core.settings import settings
from db.base import DatabaseCRUD
from schemas.films import QueryType
from schemas.query_params import PaginationParams

logger = logging.getLogger(__name__)


# Функция понадобится при внедрении зависимостей
async def get_elastic() -> AsyncElasticsearch:
    """
    Внедрение зависимостей для ручек.

    :return: Инстанс AsyncElasticSearch
    """
    es = AsyncElasticsearch(hosts=[settings.elastic_schema + settings.elastic_host + ":" + str(settings.elastic_port)])
    try:
        yield es
    finally:
        await es.close()


class ElasticCRUD(DatabaseCRUD):
    """Круд эластика."""

    async def get_list(
        self,
        model: AsyncDocument,
        page_params: PaginationParams | None = None,
        sort: str | None = None,
        fields: Union[Tuple, List] | None = None,
        path: str | None = None,
        query: Any | None = None,
        query_type: Enum | None = None,
        multiple_queries: bool | None = False,
    ):
        """Список эластик."""
        await super().get_list(model, page_params, sort, fields, path, query, query_type, multiple_queries)
        if query_type == QueryType.nested.name:
            query = model.search().using(self.db).query(query_type, path=path, query=query)
        elif query_type == QueryType.multi_match.name:
            query = model.search().using(self.db).query(query_type, query=query, fields=fields)
        elif multiple_queries:
            query = model.search().using(self.db).query(query)
        else:
            query = model.search().using(self.db)
        if sort:
            query = query.sort(sort)
        if page_params:
            start = (page_params.page - 1) * page_params.page_size
            end = page_params.page * page_params.page_size
            result = await query[start:end].execute()
            return result
        result = await query.execute()
        return result

    async def get_detail(self, model: AsyncDocument, _id: uuid.UUID):
        """Деталка эластик."""
        await super().get_detail(model, _id)
        query = model.search().using(self.db).query("match", _id=str(_id))
        result = await query.execute()
        return result
