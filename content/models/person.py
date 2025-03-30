"""Модели персоны."""

from elasticsearch_dsl import AsyncDocument, Text

from core.settings import ES_INDEX


class PersonShort(AsyncDocument):
    """Исполнитель короткая модель."""

    uuid = Text
    full_name = Text

    class Index:
        """Индекс."""

        name = ES_INDEX.person.name
