"""Асинхронный cgi: добавлен фастстрим."""

import os
from contextlib import asynccontextmanager

from django.conf import settings
from django.core.asgi import get_asgi_application
from faststream.rabbit import RabbitBroker
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

django_asgi = get_asgi_application()

# Starlette serving
broker = RabbitBroker(settings.RABBITMQ_URL)


@asynccontextmanager
async def broker_lifespan(app):
    """Лайфспан."""
    await broker.start()
    try:
        yield
    finally:
        await broker.close()


app = Starlette(
    routes=(
        Mount("/", django_asgi()),  # redirect all requests to Django
        Mount("/static", StaticFiles(directory="static"), name="static"),
    ),
    lifespan=broker_lifespan,
)
