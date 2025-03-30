"""Пользовательские кастомные исключения."""

import uuid


class UserNotFound(Exception):
    """Пользователь не найден."""

    def __init__(self, user_id: uuid.UUID, message: str = "Пользователь не найден"):
        """Инит."""
        self.user_id = user_id
        self.message = message

    def __str__(self):
        """Строковое представление."""
        return f"{self.message} -> {self.user_id}"
