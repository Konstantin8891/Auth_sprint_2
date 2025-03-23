"""Схемы фильмов."""

import uuid
from enum import Enum
from typing import List

from pydantic import BaseModel

from schemas.genres import GenreShortSchema
from schemas.persons import PersonShortSchema


class FilmWorkShortSchema(BaseModel):
    """Короткая схема для списка."""

    uuid: uuid.UUID
    title: str
    imdb_rating: float | None = None


class FilmWorkFullSchema(BaseModel):
    """Для деталки фильмов."""

    uuid: uuid.UUID
    title: str
    imdb_rating: float | None = None
    description: str | None = None
    genres: List[GenreShortSchema] | None = None
    directors: List[PersonShortSchema] | None = None
    actors: List[PersonShortSchema] | None = None
    writers: List[PersonShortSchema] | None = None


class QueryType(Enum):
    """Типы запросов elasctic."""

    multi_match = "multi_match"
    nested = "nested"
