"""Схемы жанров."""

import uuid

from pydantic import BaseModel


class GenreShortSchema(BaseModel):
    """Короткая схема жанра."""

    uuid: uuid.UUID
    name: str
