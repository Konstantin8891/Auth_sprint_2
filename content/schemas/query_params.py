"""Параметры пагинации, сортировки и фильтрации."""

import uuid
from http import HTTPStatus

from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator


class PaginationParams(BaseModel):
    """Параметры пагинации."""

    page_size: int = Field(default=50, ge=1)
    page: int = Field(default=1, ge=1)


class SortParams(BaseModel):
    """Параметры сортировки."""

    sort: str = Field()


class FilmWorkFilterParams(BaseModel):
    """Параметры фильтрации популярных фильмов."""

    genre_id: str | None = Field(None)

    @field_validator("genre_id")
    @classmethod
    def validate_genre_id(cls, value: str) -> str:
        """Валидация жанра."""
        if value:
            try:
                uuid.UUID(value)
            except ValueError:
                raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_CONTENT)
        return value


class FilmWorkSearchParams(BaseModel):
    """Параметры фильтрации для ручки поиска."""

    query: str


class PersonSearchParams(BaseModel):
    """Параметры фильтрации для ручки поиска персоны."""

    query: str
