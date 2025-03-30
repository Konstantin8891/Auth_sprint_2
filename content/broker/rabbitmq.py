"""Фастстрим."""

from faststream.rabbit import RabbitExchange
from faststream.rabbit.fastapi import RabbitRouter

from core.settings import settings

rabbit_router = RabbitRouter(settings.rabbitmq_url)

exch = RabbitExchange("amq.direct", auto_delete=False, durable=True)


def broker():
    """Брокер фастстрима."""
    return rabbit_router.broker
