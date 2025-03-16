"""Интерфейс доступа к редис."""

from redis.asyncio import Redis

from core.config import settings

# redis: Optional[Redis] = None


async def get_redis() -> Redis:
    """
    Внедрение зависимостей для ручек.

    :return: Redis
    """
    r = Redis(host=settings.redis_host, port=settings.redis_port, db=0)
    try:
        yield r
    finally:
        await r.aclose()
