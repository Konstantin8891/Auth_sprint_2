"""Конфтест и этим всё сказано."""
import logging

import pytest_asyncio
import sqlalchemy
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

import alembic
from alembic.config import Config
from core.config import settings
from core.config import settings as mocked_settings
from crud.roles import DBRole
from crud.users import DBUser
from db.postgres import get_db
from db.redis import get_redis
from main import app
from models.entity import Role, User

logger = logging.getLogger(__name__)

engine = sqlalchemy.create_engine(
    f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}/"
    f"{settings.postgres_db}",
    future=True,
)
with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
    connection.execute(text("DROP DATABASE test_db;"))
    connection.commit()
    connection.execute(text("CREATE DATABASE test_db;"))
    connection.commit()
dsn = (
    f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:5432/"
    "test_db"
)
engine = create_async_engine(dsn, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # noqa


@pytest_asyncio.fixture(autouse=True, scope="session")
async def mocked(session_mocker):
    """Замена настроек."""
    mocked_settings.postgres_db = "test_db"
    session_mocker.patch.dict("sys.modules", {"core.config.settings": mocked_settings})


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db_fixture():
    """Замена зависимостей."""

    async def get_db_override() -> AsyncSession:
        async with async_session() as session:
            yield session

    async def get_redis_override() -> Redis:
        """
        Внедрение зависимостей для ручек.

        :return: Redis
        """
        r = Redis(host=settings.redis_host, port=settings.redis_port, db=1)
        try:
            yield r
        finally:
            await r.aclose()
        # return redis

    app.dependency_overrides[get_db] = get_db_override
    app.dependency_overrides[get_redis] = get_redis_override


@pytest_asyncio.fixture(scope="session", autouse=True)
async def apply_migrations(mocked):
    """Создание и откат таблиц. Очистка редиса."""
    config = Config("alembic.ini")

    config.set_main_option(
        "sqlalchemy.url",
        (
            f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:5432/"
            "test_db"
        ),
    )
    alembic.command.upgrade(revision="heads", config=config)

    async with async_session() as db:
        yield db
        await db.rollback()

    await engine.dispose()

    r = Redis(host=settings.redis_host, port=settings.redis_port, db=2)
    await r.flushall()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def data(session_mocker, db_fixture, apply_migrations):
    """Начальные данные для тестов."""
    async with async_session() as db:
        await DBUser.create(
            db=db,
            obj_in={
                "login": "login1",
                "first_name": "User1",
                "last_name": "User1",
                "password": "password",
            },
        )

        role = await DBRole.get_by_field_name(db=db, _select=Role, field_name=Role.name, field_value="admin")
        await DBRole.create(db=db, obj_in={"name": "Role1"})

        user = await DBUser.get_by_field_name(
            db=db, field_name=User.login, field_value="login1", selection_load_options=[(User.roles,)], _select=User
        )
        await DBUser.add_role(db=db, role=role, user=user)

        await db.execute(
            text("INSERT INTO sections (id, name) VALUES ('3e828119-6ff7-42eb-a5ee-d8ac959c57df', 'Section1')")
        )

        await db.execute(
            text(
                "INSERT INTO permissions (id, can_view, can_edit, can_delete, role_id, section_id) VALUES "
                f"('41e7eca4-e982-47c8-83ea-f5231da07608', true, true, true, '{role.id}', "
                "'3e828119-6ff7-42eb-a5ee-d8ac959c57df')"
            )
        )

        await db.execute(text("INSERT INTO roles (id, name) VALUES ('dac862d4-e80e-4c17-b00d-58a269e12437', 'Role3')"))
        await db.commit()
