"""Настройки."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки."""

    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_db: str
    project_name: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int
    algorithm: str
    secret_key: str
    login_url: str
    echo: bool
    yandex_oauth_authorize: str
    yandex_oauth_token: str
    yandex_oauth_profile: str
    yandex_client_id: str
    yandex_client_secret: str
    rabbitmq_url: str

    model_config = SettingsConfigDict(
        env_file=(".env"),
    )


settings = Settings()
