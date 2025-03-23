"""Моделей жанров."""

from elasticsearch_dsl import AsyncDocument, Text

from core.settings import ES_INDEX


class Genre(AsyncDocument):
    """Жанры."""

    uuid = Text
    name = Text

    class Index:
        """Индекс."""

        name = ES_INDEX.genre.name
