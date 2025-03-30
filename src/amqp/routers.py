"""Фастстрим."""

from faststream.rabbit import RabbitExchange
from faststream.rabbit.fastapi import RabbitRouter

from core.config import settings

from .v1.users import rabbit_users_router

rabbit_master_router = RabbitRouter(settings.rabbitmq_url)

exch = RabbitExchange("amq.direct", auto_delete=False, durable=True)

rabbit_master_router.include_router(rabbit_users_router)
