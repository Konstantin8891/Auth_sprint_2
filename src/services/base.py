"""Базовый сервис."""
from abc import ABC
from typing import Any


class AbstractService(ABC):
    """Абстрактный сервис."""

    def __init__(self, db: Any, cache: Any) -> None:
        """Инициализация сервиса."""
        self.db = db
        self.cache = cache
