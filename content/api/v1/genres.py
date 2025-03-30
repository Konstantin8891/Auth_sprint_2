"""Эндпоинты жанров."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from models.genre import Genre
from schemas.genres import GenreShortSchema
from schemas.query_params import PaginationParams
from services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get("/{genre_id}", summary="Get genre by id", response_model=GenreShortSchema)
async def genre_details(genre_id: UUID, genre_service: GenreService = Depends(get_genre_service)) -> GenreShortSchema:
    """Получение жанра по id."""
    genre = await genre_service.get_by_id(_id=genre_id, model=Genre, schema=GenreShortSchema)
    return GenreShortSchema(uuid=genre.uuid, name=genre.name)


@router.get("/", summary="Gel list genres", response_model=List[GenreShortSchema])
async def genre_all(
    pagination: PaginationParams = Depends(), genre_service: GenreService = Depends(get_genre_service)
) -> List[GenreShortSchema]:
    """Получение всех жанров."""
    genres = await genre_service.get_all(pagination)
    return genres
