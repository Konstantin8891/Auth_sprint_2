"""Мэйн."""
import logging
from logging.config import dictConfig

from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from amqp.routers import rabbit_master_router
from api.urls import router
from core.config import settings
from core.logger import LOGGING

dictConfig(LOGGING)

logger = logging.getLogger(settings.project_name)


def configure_tracer() -> None:
    """Конфигурирование трассировщика."""
    resource = Resource(attributes={SERVICE_NAME: "auth-service"})
    trace.set_tracer_provider(TracerProvider(resource=resource))
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=settings.jaeger_host,
                agent_port=settings.jaeger_port,
            )
        )
    )
    # Чтобы видеть трейсы в консоли
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


if settings.enable_tracer:
    configure_tracer()

app = FastAPI(
    title=settings.project_name,
    docs_url="/api/pumpkin_auth/openapi",
    openapi_url="/api/pumpkin_auth/openapi.json",
    default_response_class=ORJSONResponse,
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


app.include_router(router, prefix="/api/pumpkin_auth")
app.include_router(rabbit_master_router, prefix="/amqp")
add_pagination(app)
