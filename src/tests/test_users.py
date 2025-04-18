"""Тесты пользователей."""

from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.mark.parametrize(
    "payload_data, expected_answer",
    [
        ({}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
        (
            {
                "login": "login1",
            },
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
        ({"password": "password"}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
        ({"login": "login20", "password": "password20"}, {"status": HTTPStatus.OK, "login": "login20"}),
    ],
)
async def test_patch_user(payload_data, expected_answer):
    """Тест редактирования пользователя."""
    client = TestClient(app)

    response = client.patch(
        "/api/auth/v1/users",
        json=payload_data,
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9b"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    response = client.post(
        "/api/auth/v1/auth/login",
        json={"login": "login1", "password": "password"},
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9b"},
    )
    data = response.json()

    access = data.get("access_token")

    response = client.patch(
        "/api/auth/v1/users",
        headers={"Authorization": f"Bearer {access}", "X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9b"},
        json=payload_data,
    )

    data = response.json()

    assert response.status_code == expected_answer.get("status")
    if response.status_code == HTTPStatus.OK:
        response = client.post(
            "/api/auth/v1/auth/login",
            json={"login": payload_data["login"], "password": payload_data["password"]},
            headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9b"},
        )
        assert response.status_code == HTTPStatus.OK


async def test_login_history():
    """Тестирование истории логинов."""
    client = TestClient(app)

    response = client.get(
        "/api/auth/v1/users/login_history",
        params={"page": 1, "size": 10},
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9b"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    response = client.post(
        "/api/auth/v1/auth/login",
        json={"login": "login20", "password": "password20"},
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9b"},
    )
    data = response.json()

    access = data.get("access_token")

    response = client.get(
        "/api/auth/v1/users/login_history",
        headers={"Authorization": f"Bearer {access}", "X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9b"},
        params={"page": 1, "size": 10},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert data.get("total") is not None
    assert data.get("page") is not None
    assert data.get("size") is not None
    assert data.get("pages") is not None
    assert data.get("items") is not None
