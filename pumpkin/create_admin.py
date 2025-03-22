"""Создание админа."""

import asyncio
import uuid
from http import HTTPStatus

import typer
from fastapi import HTTPException
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from db.postgres import async_session

app = typer.Typer()


async def create_admin_task(login: str, first_name: str, last_name: str, password: str):
    """Создание админа метод."""
    async with async_session() as db:
        password = generate_password_hash(password)
        _id = uuid.uuid4()
        query = text(f"SELECT * FROM users WHERE login='{login}'")
        result = await db.execute(query)
        result = result.scalars().first()
        if result:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Login already exists")
        query = text(
            "INSERT INTO users (id, login, password, first_name, last_name) "
            f"VALUES ('{_id}', '{login}', '{password}', '{first_name}', '{last_name}')"
        )
        await db.execute(query)
        await db.commit()
        query = text(
            f"INSERT INTO userrole (user_id, role_id) VALUES ('{_id}', " "'b845266b-812a-49d5-8945-8426f21b789f')"
        )
        await db.execute(query)
        await db.commit()


@app.command()
def create_admin(login: str, first_name: str, last_name: str, password: str):
    """Создание админа команда."""
    asyncio.run(create_admin_task(login, first_name, last_name, password))


if __name__ == "__main__":
    app()
