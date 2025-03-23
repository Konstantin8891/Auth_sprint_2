"""Абстрактный класс базы данных."""
from abc import abstractmethod
from typing import Any


class DatabaseCRUD:
    """Абстрактный класс работы с базой данных."""

    def __init__(self, db: Any):
        """Инициализация."""
        self.db = db

    @abstractmethod
    async def get_list(self, *args, **kwargs):
        """Список сущностей."""
        pass

    @abstractmethod
    async def get_detail(self, *args, **kwargs):
        """Детальная карточка."""
        pass
