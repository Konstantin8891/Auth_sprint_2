"""Auth."""
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.mark.parametrize(
    "payload_data, expected_answer",
    [
        (
            {"login": "login2", "last_name": "User2", "password": "password"},
            {"status": HTTPStatus.UNPROCESSABLE_CONTENT},
        ),
        (
            {"first_name": "User2", "last_name": "User2", "password": "password"},
            {"status": HTTPStatus.UNPROCESSABLE_CONTENT},
        ),
        (
            {"login": "login2", "first_name": "User2", "password": "password"},
            {"status": HTTPStatus.UNPROCESSABLE_CONTENT},
        ),
        (
            {"login": "login2", "first_name": "User2", "last_name": "User2"},
            {"status": HTTPStatus.UNPROCESSABLE_CONTENT},
        ),
        (
            {"login": "login2", "first_name": "User2", "last_name": "User2", "password": "password"},
            {"status": HTTPStatus.CREATED, "first_name": "User2", "last_name": "User2"},
        ),
        (
            {"login": "login1", "first_name": "User2", "last_name": "User2", "password": "password"},
            {"status": HTTPStatus.BAD_REQUEST},
        ),
    ],
)
async def test_signup(payload_data, expected_answer):
    """Регистрация пользователя."""
    client = TestClient(app)

    response = client.post(
        "/api/auth/v1/auth/signup", json=payload_data, headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"}
    )
    data = response.json()

    assert response.status_code == expected_answer.get("status")
    if expected_answer.get("first_name"):
        assert data["first_name"] == "User2"
        assert data["id"] is not None
    if expected_answer.get("last_name"):
        assert data["last_name"] == "User2"


@pytest.mark.parametrize(
    "payload_data, expected_answer",
    [
        ({"password": "password"}, {"status": HTTPStatus.UNPROCESSABLE_CONTENT}),
        ({"login": "login1"}, {"status": HTTPStatus.UNPROCESSABLE_CONTENT}),
        ({"login": "login1", "password": "bjbkjjk"}, {"status": HTTPStatus.UNAUTHORIZED}),
        ({"login": "login1", "password": "password"}, {"status": HTTPStatus.OK}),
    ],
)
async def test_login(payload_data, expected_answer):
    """Логин."""
    client = TestClient(app)

    response = client.post(
        "/api/auth/v1/auth/login", json=payload_data, headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"}
    )
    data = response.json()

    assert response.status_code == expected_answer.get("status")
    if expected_answer.get("status") == HTTPStatus.OK:
        assert data["access_token"] is not None
        assert data["refresh_token"] is not None


async def test_refresh():
    """Рефреш."""
    client = TestClient(app)

    response = client.post(
        "/api/auth/v1/auth/login",
        json={"login": "login1", "password": "password"},
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )
    data = response.json()

    wrong_refresh = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDE5ODQ4MDIsInN1YiI6ImNjZjAxNjZhLTRmZDgtMTFlYS1hM2Q3LTVjYWE"
        "4MTdlZjA5YyIsInR5cGUiOiJyZWZyZXNoIn0.tLbSwb2SV2I4dMkVH571tbh8ZY-n2MeWpPDTM3cpZc4"
    )

    refresh = data.get("refresh_token")

    response = client.post(
        "/api/auth/v1/auth/refresh",
        json={"refresh_token": wrong_refresh},
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    response = client.post(
        "/api/auth/v1/auth/refresh",
        json={"refresh_token": refresh},
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )

    assert response.status_code == HTTPStatus.OK

    data = response.json()

    assert data.get("access_token") is not None
    assert data.get("refresh_token") is not None


async def test_logout():
    """Логаут."""
    client = TestClient(app)

    response = client.post(
        "/api/auth/v1/auth/login",
        json={"login": "login1", "password": "password"},
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )
    data = response.json()

    refresh = data.get("refresh_token")

    response = client.delete(
        "/api/auth/v1/auth/logout",
        headers={
            "Authorization": f"Bearer {data.get('access_token')}",
            "X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a",
        },
    )

    wrong_refresh = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDE5ODQ4MDIsInN1YiI6ImNjZjAxNjZhLTRmZDgtMTFlYS1hM2Q3LTVjYWE"
        "4MTdlZjA5YyIsInR5cGUiOiJyZWZyZXNoIn0.tLbSwb2SV2I4dMkVH571tbh8ZY-n2MeWpPDTM3cpZc4"
    )

    response = client.post(
        "/api/auth/v1/auth/refresh",
        json={"refresh_token": wrong_refresh},
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    response = client.post(
        "/api/auth/v1/auth/refresh",
        json={"refresh_token": refresh},
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


async def test_logout_all():
    """Выйти на всех устройствах."""
    client = TestClient(app)

    response = client.post(
        "/api/auth/v1/auth/login",
        json={"login": "login1", "password": "password"},
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )
    data = response.json()

    refresh = data.get("refresh_token")

    response = client.delete(
        "/api/auth/v1/auth/logout/all",
        headers={
            "Authorization": f"Bearer {data.get('access_token')}",
            "X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a",
        },
    )

    wrong_refresh = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDE5ODQ4MDIsInN1YiI6ImNjZjAxNjZhLTRmZDgtMTFlYS1hM2Q3LTVjYWE"
        "4MTdlZjA5YyIsInR5cGUiOiJyZWZyZXNoIn0.tLbSwb2SV2I4dMkVH571tbh8ZY-n2MeWpPDTM3cpZc4"
    )

    response = client.post(
        "/api/auth/v1/auth/refresh",
        json={"refresh_token": wrong_refresh},
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    response = client.post(
        "/api/auth/v1/auth/refresh",
        json={"refresh_token": refresh},
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
