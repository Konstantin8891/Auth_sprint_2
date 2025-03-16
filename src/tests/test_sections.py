"""Тесты разделов."""

from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.mark.parametrize(
    "payload_data, expected_answer",
    [
        ({}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
        ({"name": "Section1"}, {"status": HTTPStatus.BAD_REQUEST}),
        ({"name": "Section2"}, {"status": HTTPStatus.CREATED, "name": "Section2"}),
    ],
)
async def test_create_section(payload_data, expected_answer):
    """Тест создания раздела."""
    client = TestClient(app)

    response = client.post("/api/v1/sections", json=payload_data)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    response = client.post("/api/v1/auth/login", json={"login": "login1", "password": "password"})
    data = response.json()

    access = data.get("access_token")

    response = client.post("/api/v1/sections", headers={"Authorization": f"Bearer {access}"}, json=payload_data)

    data = response.json()

    assert response.status_code == expected_answer.get("status")
    if response.status_code == HTTPStatus.CREATED:
        assert data.get("name") == expected_answer["name"]


async def test_get_sections():
    """Получение разделов."""
    client = TestClient(app)

    response = client.get("/api/v1/sections")

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    response = client.post("/api/v1/auth/login", json={"login": "login1", "password": "password"})
    data = response.json()

    access = data.get("access_token")

    response = client.get("/api/v1/sections", headers={"Authorization": f"Bearer {access}"})
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(data) == 2
