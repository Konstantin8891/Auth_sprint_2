"""Мэйн."""
import logging
from logging.config import dictConfig

from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from amqp.routers import rabbit_master_router  # noqa
from api.urls import router
from broker.rabbitmq import rabbit_router
from core.config import settings
from core.logger import LOGGING


@rabbit_router.subscriber("test")
async def hello(msg: str):
    """Тестовая ручка."""
    return {"response": "Hello, Rabbit!"}


@rabbit_router.after_startup
async def test(app: FastAPI):
    """После старта кролика."""
    await rabbit_router.broker.publish("Hello!", "test")


dictConfig(LOGGING)

logger = logging.getLogger(settings.project_name)

#
# def configure_tracer() -> None:
#     trace.set_tracer_provider(TracerProvider())
#     trace.get_tracer_provider().add_span_processor(
#         BatchSpanProcessor(
#             JaegerExporter(
#                 # agent_host_name='jaeger',
#                 agent_host_name='localhost',
#                 agent_port=6831,
#             )
#         )
#     )
#     # Чтобы видеть трейсы в консоли
#     trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
#     # tracer = TracerProvider()
#     # trace.set_tracer_provider(tracer)
#     #
#     # tracer.add_span_processor(
#     #     BatchSpanProcessor(OTLPSpanExporter(endpoint="http://jaeger-collector:4318/v1/traces"))
#     # )
#     #
#     # # override logger format which with trace id and span id
#     # if log_correlation:
#     #     LoggingInstrumentor().instrument(set_logging_format=True)
#     #
#     # FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer)
#
#
# configure_tracer()


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


configure_tracer()


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)
FastAPIInstrumentor.instrument_app(app)


@app.middleware("http")
async def before_request(request: Request, call_next):
    """Чек хедеров: request-id."""
    response = await call_next(request)
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "X-Request-Id is required"})
    tracer = trace.get_tracer(__name__)
    # with tracer.start_span('TestSpan') as span:
    # span.log_kv({'event': 'test message', 'life': 42})
    #
    # with tracer.start_span('ChildSpan', child_of=span) as child_span:
    #     child_span.log_kv({'event': 'down below'})
    span = tracer.start_span()
    span.set_attribute("http.request_id", request_id)
    span.end()
    return response


app.include_router(rabbit_master_router, prefix="/amqp")
app.include_router(router, prefix="/api")
add_pagination(app)
