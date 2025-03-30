"""Эндпоинты для фильмов."""

from fastapi import APIRouter

from .v1.films import router as v1_movies_router
from .v1.genres import router as v1_genres_router
from .v1.healthcheck import router as v1_healthcheck
from .v1.persons import router as v1_persons_router

router = APIRouter()

router.include_router(v1_movies_router, tags=["films"], prefix="/v1/films")
router.include_router(v1_genres_router, tags=["genres"], prefix="/v1/genres")
router.include_router(v1_persons_router, tags=["persons"], prefix="/v1/persons")
router.include_router(v1_healthcheck, tags=["healthcheck"], prefix="/healthcheck")
