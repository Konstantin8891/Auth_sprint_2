"""Схемы для действующих лиц."""

import uuid
from enum import Enum
from typing import List

from pydantic import BaseModel


class Role(Enum):
    """Роли персоны в фильмах."""

    writer = "writer"
    director = "director"
    actor = "actor"


class PersonShortSchema(BaseModel):
    """Короткая схема персоны."""

    uuid: uuid.UUID
    full_name: str


class FilmInPersonSchema(BaseModel):
    """Схема фильмов в схеме персоны."""

    uuid: uuid.UUID
    roles: List[Role]


class PersonFullSchema(BaseModel):
    """Полная схема персоны."""

    uuid: uuid.UUID
    full_name: str
    films: List[FilmInPersonSchema]
