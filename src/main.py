"""Мэйн."""
import logging
from logging.config import dictConfig

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination

from api.urls import router
from core.config import settings
from core.logger import LOGGING

dictConfig(LOGGING)

logger = logging.getLogger(settings.project_name)

app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

app.include_router(router, prefix="/api")
add_pagination(app)
