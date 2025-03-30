"""Модели, связанные с фильмами."""

from typing import List

from elasticsearch_dsl import AsyncDocument, Float, Nested, Text

from core.settings import ES_INDEX
from models.genre import Genre
from models.person import PersonShort


class FilmWork(AsyncDocument):
    """Кинопроизведение."""

    uuid = Text
    title = Text
    imdb_rating = Float
    description = Text
    genre = List[Nested(Genre)]
    actors = List[Nested(PersonShort)]
    writers = List[Nested(PersonShort)]
    directors = List[Nested(PersonShort)]

    class Index:
        """Индекс."""

        name = ES_INDEX.movies.name
