"""Точка входа в приложение."""

import logging
from contextlib import asynccontextmanager
from http import HTTPStatus
from logging.config import dictConfig

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, ORJSONResponse
from redis.asyncio import Redis

from api.urls import router
from broker.rabbitmq import rabbit_router
from core.logger import LOGGING
from core.settings import settings
from db import elastic, redis


@rabbit_router.subscriber("test")
async def hello(msg: str):
    """Тестовая ручка."""
    return {"response": "Hello, Rabbit!"}


@rabbit_router.after_startup
async def test(app: FastAPI):
    """Приветственное сообщение."""
    await rabbit_router.broker.publish("Hello!", "test")


dictConfig(LOGGING)
logger = logging.getLogger("content")


# On events deprecated use lifespan instead
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan вместо устаревшего on_event.

    :param app: Приложение FastAPI
    :return: None
    """
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    elastic.es = AsyncElasticsearch(hosts=[f"{settings.elastic_schema}{settings.elastic_host}:{settings.elastic_port}"])
    yield
    # Clean up the ML models and release the resources
    await redis.redis.close()
    await elastic.es.close()


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(rabbit_router, prefix="/amqp")
app.include_router(router, prefix="/api/content")


@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, exc: Exception):
    """Обработчик исключений."""
    logger.error(f"Failed method {request.method} at URL {request.url}. Exception message is {exc!r}.")
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={"message": str(exc)},
    )
