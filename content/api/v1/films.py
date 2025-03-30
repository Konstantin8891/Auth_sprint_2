"""Ручки фильмов."""

import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, Request
from faststream.rabbit import RabbitBroker

from broker.rabbitmq import broker
from models.movies import FilmWork
from schemas.films import FilmWorkFullSchema, FilmWorkShortSchema
from schemas.query_params import FilmWorkFilterParams, FilmWorkSearchParams, PaginationParams, SortParams
from services.films import FilmService, get_film_service

router = APIRouter()


@router.get("", summary="Get popular films", response_model=List[FilmWorkShortSchema])
async def get_films(
    request: Request,
    rabbit_broker: Annotated[RabbitBroker, Depends(broker)],
    sort_params: SortParams = Depends(),
    page_params: PaginationParams = Depends(),
    filter_params: FilmWorkFilterParams = Depends(),
    film_service: FilmService = Depends(get_film_service),
) -> List[FilmWorkShortSchema]:
    """Получение фильмов."""
    result = await film_service.get_films(
        page_params=page_params,
        sort_params=sort_params,
        filter_params=filter_params,
        broker=rabbit_broker,
        request=request,
    )
    return result


@router.get("/search/", summary="Search films", response_model=List[FilmWorkShortSchema])
async def search_films(
    page_params: PaginationParams = Depends(),
    search_params: FilmWorkSearchParams = Depends(),
    film_service: FilmService = Depends(get_film_service),
) -> List[FilmWorkShortSchema]:
    """Поиск фильмов."""
    result = await film_service.search(page_params=page_params, search_params=search_params)
    return result


@router.get("/{film_id}", summary="Get film detail", response_model=FilmWorkFullSchema)
async def get_film_detail(
    film_id: uuid.UUID, film_service: FilmService = Depends(get_film_service)
) -> FilmWorkFullSchema:
    """Деталка фильма."""
    result = await film_service.get_by_id(_id=film_id, model=FilmWork, schema=FilmWorkFullSchema)
    return result
