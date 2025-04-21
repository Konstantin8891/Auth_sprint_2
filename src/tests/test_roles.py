"""Тест ролей."""

import logging
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from main import app

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "payload_data, expected_answer",
    [
        ({"name": 111}, {"status": HTTPStatus.UNPROCESSABLE_CONTENT}),
        ({"name": "Role2"}, {"status": HTTPStatus.UNPROCESSABLE_CONTENT}),
        (
            {
                "name": "Role2",
                "permissions": [
                    {"can_edit": True, "can_delete": True, "section_id": "3e828119-6ff7-42eb-a5ee-d8ac959c57df"}
                ],
            },
            {"status": HTTPStatus.UNPROCESSABLE_CONTENT},
        ),
        (
            {
                "name": "Role2",
                "permissions": [
                    {"can_view": True, "can_delete": True, "section_id": "3e828119-6ff7-42eb-a5ee-d8ac959c57df"}
                ],
            },
            {"status": HTTPStatus.UNPROCESSABLE_CONTENT},
        ),
        (
            {
                "name": "Role2",
                "permissions": [
                    {"can_view": True, "can_edit": True, "section_id": "3e828119-6ff7-42eb-a5ee-d8ac959c57df"}
                ],
            },
            {"status": HTTPStatus.UNPROCESSABLE_CONTENT},
        ),
        (
            {"name": "Role2", "permissions": [{"can_view": True, "can_edit": True, "can_delete": True}]},
            {"status": HTTPStatus.UNPROCESSABLE_CONTENT},
        ),
        (
            {
                "name": "Role2",
                "permissions": [
                    {
                        "can_view": True,
                        "can_edit": True,
                        "can_delete": True,
                        "section_id": "3e828119-6ff7-42eb-a5ee-d8ac959c57df",
                    }
                ],
            },
            {
                "status": HTTPStatus.OK,
                "name": "Role2",
                "permissions": [
                    {
                        "can_view": True,
                        "can_edit": True,
                        "can_delete": True,
                        "section": {"id": "3e828119-6ff7-42eb-a5ee-d8ac959c57df", "name": "Section1"},
                    }
                ],
            },
        ),
    ],
)
async def test_create_role(payload_data, expected_answer):
    """Создание роли."""
    client = TestClient(app)

    response = client.post(
        "/api/auth/v1/auth/login",
        json={"login": "login1", "password": "password"},
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )
    data = response.json()

    access = data.get("access_token")

    response = client.post(
        "/api/auth/v1/roles",
        json=payload_data,
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    response = client.post(
        "/api/auth/v1/roles",
        json=payload_data,
        headers={"Authorization": f"Bearer {access}", "X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )
    data = response.json()

    assert response.status_code == expected_answer.get("status")
    if expected_answer.get("name"):
        assert data["name"] == expected_answer.get("name")
        assert data["id"] is not None
        assert data["permissions"] == expected_answer.get("permissions")


async def test_get_roles():
    """Получение ролей."""
    client = TestClient(app)

    response = client.get("/api/auth/v1/roles", headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"})

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    response = client.post(
        "/api/auth/v1/auth/login",
        json={"login": "login1", "password": "password"},
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )
    data = response.json()

    access = data.get("access_token")

    response = client.get(
        "/api/auth/v1/roles",
        headers={"Authorization": f"Bearer {access}", "X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )

    assert response.status_code == HTTPStatus.OK

    data = response.json()

    assert len(data) == 5


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        ({"role_name": "hjbjbj"}, {"status": HTTPStatus.OK, "name": "hjbjbj", "has": False}),
        ({"role_name": "admin"}, {"status": HTTPStatus.OK, "name": "admin", "has": True}),
    ],
)
async def test_check_role(query_data, expected_answer):
    """Проверка наличия роли у пользователя."""
    client = TestClient(app)

    response = client.get(
        "/api/auth/v1/roles/user",
        params=query_data,
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    response = client.post(
        "/api/auth/v1/auth/login",
        json={"login": "login1", "password": "password"},
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )
    data = response.json()

    access = data.get("access_token")

    response = client.get(
        "/api/auth/v1/roles/user",
        headers={"Authorization": f"Bearer {access}", "X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
        params=query_data,
    )

    assert response.status_code == expected_answer.get("status")

    data = response.json()

    assert data["name"] == expected_answer.get("name")
    assert data["has"] == expected_answer.get("has")


@pytest.mark.parametrize(
    "payload_data, expected_answer",
    [
        ({"delete": False}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
        ({"name": "Role1"}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
        ({"name": "1111", "delete": False}, {"status": HTTPStatus.BAD_REQUEST}),
        ({"name": "Role1", "delete": "1111"}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
        ({"name": "Role1", "delete": True}, {"status": HTTPStatus.BAD_REQUEST}),
        ({"name": "Role1", "delete": False}, {"status": HTTPStatus.OK}),
        ({"name": "Role1", "delete": False}, {"status": HTTPStatus.BAD_REQUEST}),
        ({"name": "Role1", "delete": True}, {"status": HTTPStatus.OK}),
    ],
)
async def test_patch_user_role(payload_data, expected_answer):
    """Редактирование ролей пользователя."""
    client = TestClient(app)

    response = client.patch(
        "/api/auth/v1/roles/user",
        json=payload_data,
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    response = client.post(
        "/api/auth/v1/auth/login",
        json={"login": "login1", "password": "password"},
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )
    data = response.json()

    access = data.get("access_token")

    response = client.patch(
        "/api/auth/v1/roles/user",
        headers={"Authorization": f"Bearer {access}", "X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
        json=payload_data,
    )

    assert response.status_code == expected_answer.get("status")


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"section_name": "Section1"},
            {
                "status": HTTPStatus.OK,
                "can_view": True,
                "can_edit": True,
                "can_delete": True,
                "section": {"id": "3e828119-6ff7-42eb-a5ee-d8ac959c57df", "name": "Section1"},
            },
        ),
        ({"section_name": "Section2"}, {"status": HTTPStatus.BAD_REQUEST}),
        ({"qqqqq": "qqqqq"}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
    ],
)
async def test_check_permission(query_data, expected_answer):
    """Получение пермишена."""
    client = TestClient(app)

    response = client.get(
        "/api/auth/v1/roles/permissions",
        params=query_data,
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    response = client.post(
        "/api/auth/v1/auth/login",
        json={"login": "login1", "password": "password"},
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )
    data = response.json()

    access = data.get("access_token")

    response = client.get(
        "/api/auth/v1/roles/permissions",
        headers={"Authorization": f"Bearer {access}", "X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
        params=query_data,
    )

    data = response.json()

    assert response.status_code == expected_answer.get("status")
    if expected_answer.get("status") == HTTPStatus.OK:
        del expected_answer["status"]
        assert expected_answer == data


@pytest.mark.parametrize(
    "role_id, expected_answer",
    [
        (
            "dac862d4-e80e-4c17-b00d-58a269e12437",
            {"status": HTTPStatus.OK, "id": "dac862d4-e80e-4c17-b00d-58a269e12437", "name": "Role3", "permissions": []},
        ),
        ("4084f286-7d4d-4818-aa92-90f7ecedc97b", {"status": HTTPStatus.NOT_FOUND}),
    ],
)
async def test_get_role(role_id, expected_answer):
    """Получение роли."""
    client = TestClient(app)

    response = client.get(
        f"/api/auth/v1/roles/{role_id}", headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    response = client.post(
        "/api/auth/v1/auth/login",
        json={"login": "login1", "password": "password"},
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )
    data = response.json()

    access = data.get("access_token")

    response = client.get(
        f"/api/auth/v1/roles/{role_id}",
        headers={"Authorization": f"Bearer {access}", "X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )

    data = response.json()

    assert response.status_code == expected_answer.get("status")
    if expected_answer.get("status") == HTTPStatus.OK:
        del expected_answer["status"]
        assert expected_answer == data


@pytest.mark.parametrize(
    "role_id, payload_data, expected_answer",
    [
        (
            "dac862d4-e80e-4c17-b00d-58a269e12437",
            {
                "name": "Patch",
                "permissions": [
                    {
                        "can_view": False,
                        "can_edit": False,
                        "can_delete": False,
                        "section_id": "3e828119-6ff7-42eb-a5ee-d8ac959c57df",
                    }
                ],
            },
            {
                "status": HTTPStatus.OK,
                "id": "dac862d4-e80e-4c17-b00d-58a269e12437",
                "name": "Patch",
                "permissions": [
                    {
                        "can_view": False,
                        "can_edit": False,
                        "can_delete": False,
                        "section": {"id": "3e828119-6ff7-42eb-a5ee-d8ac959c57df", "name": "Section1"},
                    }
                ],
            },
        ),
        (
            "dac862d4-e80e-4c17-b00d-58a269e12437",
            {
                "name": "Patch",
                "permissions": [
                    {
                        "can_view": False,
                        "can_edit": False,
                        "can_delete": False,
                        "section_id": "80416a87-d64b-4cba-ae33-6db1f0366ce7",
                    }
                ],
            },
            {"status": HTTPStatus.BAD_REQUEST},
        ),
        (
            "d3930fab-4cb6-4e49-b95b-7d6ced8e39c7",
            {
                "name": "Patch",
                "permissions": [
                    {
                        "can_view": False,
                        "can_edit": False,
                        "can_delete": False,
                        "section_id": "80416a87-d64b-4cba-ae33-6db1f0366ce7",
                    }
                ],
            },
            {"status": HTTPStatus.NOT_FOUND},
        ),
        (
            "dac862d4-e80e-4c17-b00d-58a269e12437",
            {
                "name": "Patch",
                "permissions": [
                    {
                        "can_edit": False,
                        "can_delete": False,
                        "section_id": "3e828119-6ff7-42eb-a5ee-d8ac959c57df",
                    }
                ],
            },
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
        (
            "dac862d4-e80e-4c17-b00d-58a269e12437",
            {
                "permissions": [
                    {
                        "can_view": False,
                        "can_edit": False,
                        "can_delete": False,
                        "section_id": "3e828119-6ff7-42eb-a5ee-d8ac959c57df",
                    }
                ]
            },
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
        (
            "dac862d4-e80e-4c17-b00d-58a269e12437",
            {
                "name": "Patch",
                "permissions": [
                    {
                        "can_view": False,
                        "can_delete": False,
                        "section_id": "3e828119-6ff7-42eb-a5ee-d8ac959c57df",
                    }
                ],
            },
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
        (
            "dac862d4-e80e-4c17-b00d-58a269e12437",
            {
                "name": "Patch",
                "permissions": [
                    {
                        "can_view": False,
                        "can_edit": False,
                        "section_id": "3e828119-6ff7-42eb-a5ee-d8ac959c57df",
                    }
                ],
            },
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
        (
            "dac862d4-e80e-4c17-b00d-58a269e12437",
            {
                "name": "Patch",
                "permissions": [
                    {
                        "can_view": False,
                        "can_edit": False,
                        "can_delete": False,
                    }
                ],
            },
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
    ],
)
async def test_patch_role(role_id, payload_data, expected_answer):
    """Редактирвоание роли."""
    client = TestClient(app)

    response = client.get(
        f"/api/auth/v1/roles/{role_id}", headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    response = client.post(
        "/api/auth/v1/auth/login",
        json={"login": "login1", "password": "password"},
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )
    data = response.json()

    access = data.get("access_token")

    response = client.patch(
        f"/api/auth/v1/roles/{role_id}",
        headers={"Authorization": f"Bearer {access}", "X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
        json=payload_data,
    )

    data = response.json()

    assert response.status_code == expected_answer.get("status")
    if expected_answer.get("status") == HTTPStatus.OK:
        assert expected_answer.get("name") == data["name"]


@pytest.mark.parametrize(
    "role_id, expected_answer",
    [
        ("4084f286-7d4d-4818-aa92-90f7ecedc97b", {"status": HTTPStatus.NOT_FOUND}),
        ("dac862d4-e80e-4c17-b00d-58a269e12437", {"status": HTTPStatus.NO_CONTENT}),
        ("dac862d4-e80e-4c17-b00d-58a269e12437", {"status": HTTPStatus.NOT_FOUND}),
    ],
)
async def test_delete_role(role_id, expected_answer):
    """Удаление роли."""
    client = TestClient(app)

    response = client.get(
        f"/api/auth/v1/roles/{role_id}", headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    response = client.post(
        "/api/auth/v1/auth/login",
        json={"login": "login1", "password": "password"},
        headers={"X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )
    data = response.json()

    access = data.get("access_token")

    response = client.delete(
        f"/api/auth/v1/roles/{role_id}",
        headers={"Authorization": f"Bearer {access}", "X-Request-Id": "0x62ba858d7719d51d6a3255394cdd8b9a"},
    )

    assert response.status_code == expected_answer.get("status")
