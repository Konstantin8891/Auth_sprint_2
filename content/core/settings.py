"""Настройки."""

import os
from enum import Enum
from logging import config as logging_config

from pydantic_settings import BaseSettings, SettingsConfigDict

from core.logger import LOGGING


class Settings(BaseSettings):
    """Переменные окружения."""

    project_name: str
    redis_host: str
    redis_port: int
    elastic_host: str
    elastic_port: int
    elastic_schema: str
    cache_expire_in_seconds: int
    rabbitmq_url: str
    algorithm: str
    secret_key: str

    model_config = SettingsConfigDict(
        env_file=(".env",),
    )


class ES_INDEX(Enum):
    """Elasticsearch index."""

    movies = "movies"
    person = "person"
    genre = "genre"


logging_config.dictConfig(LOGGING)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

settings = Settings()
