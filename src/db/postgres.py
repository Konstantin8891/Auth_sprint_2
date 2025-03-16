"""Постгрес."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import settings

# Создаём базовый класс для будущих моделей
Base = declarative_base()
# Создаём движок
# Настройки подключения к БД передаём из переменных окружения, которые заранее загружены в файл настроек
dsn = (
    f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}/"
    f"{settings.postgres_db}"
)
engine = create_async_engine(dsn, future=True, echo=settings.echo)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # noqa


async def get_db():
    """Подключение к постгрес."""
    async with async_session() as session:
        yield session
