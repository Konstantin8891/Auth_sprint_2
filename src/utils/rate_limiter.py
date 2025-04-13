"""Ограничитель запросов."""

import datetime

import redis

from core.config import settings

redis_conn = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=1)


def rate_limiter(user):
    """Ограничитель запросов."""
    pipe = redis_conn.pipeline()
    now = datetime.datetime.now()
    key = f"{user}:{now.minute}"
    pipe.incr(key)
    pipe.expire(key, settings.exp_rate_limiter)
    result = pipe.execute()
    request_number = result[0]
    if request_number > settings.request_limit_per_minute:
        return True
    else:
        return False
