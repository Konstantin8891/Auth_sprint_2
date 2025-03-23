"""Интерфейс доступа к редис."""

from redis.asyncio import Redis

redis: Redis | None = None


# Функция понадобится при внедрении зависимостей
async def get_redis() -> Redis:
    """
    Внедрение зависимостей для ручек.

    :return: Redis
    """
    return redis
