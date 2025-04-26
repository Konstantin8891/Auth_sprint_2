"""Базовый сервис."""
from abc import ABC, abstractmethod
from typing import Any


class AbstractService(ABC):
    """Абстрактный сервис."""

    def __init__(self, db: Any, cache: Any) -> None:
        """Инициализация сервиса."""
        self.db = db
        self.cache = cache


class SocialAbstractService(AbstractService):
    """Абстрактный сервис."""

    @abstractmethod
    def get_link(self, provider: Any):
        """Получение ссылки провайдера."""
        pass

    @abstractmethod
    def get_tokens(self, provider: Any, *args, **kwargs):
        """ПОлучение токенов."""
        pass
