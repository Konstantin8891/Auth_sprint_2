"""Точка входа в приложение."""

import logging
from contextlib import asynccontextmanager
from http import HTTPStatus
from logging.config import dictConfig

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, ORJSONResponse
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
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


def configure_tracer() -> None:
    """Конфигурирование трассировщика."""
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name="all-in-one",
                agent_port=6831,
            )
        )
    )
    # Чтобы видеть трейсы в консоли
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


if settings.enable_tracer:
    configure_tracer()


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
    docs_url="/api/content/openapi",
    openapi_url="/api/content/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)
if settings.enable_tracer:
    FastAPIInstrumentor.instrument_app(app)


@app.middleware("http")
async def before_request(request: Request, call_next):
    """Чек хедеров: request-id."""
    response = await call_next(request)
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "X-Request-Id is required"})
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span("auth")
    span.set_attribute("http.request_id", request_id)
    span.end()
    return response


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
