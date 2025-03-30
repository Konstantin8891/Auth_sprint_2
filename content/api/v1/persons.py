"""Ендоинты людей."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from models.person import PersonShort
from schemas.persons import FilmInPersonSchema, PersonFullSchema, PersonShortSchema
from schemas.query_params import PaginationParams, PersonSearchParams
from services.films import FilmService, get_film_service
from services.person import PersonService, get_person_service

router = APIRouter()


@router.get("/search", summary="Search persons", response_model=List[PersonFullSchema])
async def search_persons(
    page_params: PaginationParams = Depends(),
    search_params: PersonSearchParams = Depends(),
    person_service: PersonService = Depends(get_person_service),
) -> List[PersonFullSchema]:
    """Поиск людей."""
    persons = await person_service.search(search_params, page_params)
    return persons


@router.get("/{person_id}", summary="Get person by id", response_model=PersonFullSchema)
async def person_details(
    person_id: UUID,
    person_service: PersonService = Depends(get_person_service),
) -> PersonFullSchema:
    """Информация о человеке по его id."""
    person = await person_service.get_by_id(_id=person_id, model=PersonShort, schema=PersonShortSchema)
    return person


@router.get("/{person_id}/film", summary="Get film by person id", response_model=List[FilmInPersonSchema])
async def person_film(
    person_id: UUID,
    film_service: FilmService = Depends(get_film_service),
) -> List[FilmInPersonSchema]:
    """Фильмы человека по его id."""
    films = await film_service.get_films_by_person(person_id)
    return films
