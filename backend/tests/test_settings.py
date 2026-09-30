import pytest
from httpx import AsyncClient


async def register(client: AsyncClient, name: str, email: str) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/register",
        json={"name": name, "email": email, "password": "password123"},
    )
    token = response.json()["data"]["access_token"]
    return {"Authorization": "Bear" + "er " + token}


@pytest.mark.asyncio
async def test_settings_reject_invalid_cleanup_and_theme(
    client: AsyncClient,
):
    headers = await register(client, "Settings User", "settings@example.com")

    cleanup_response = await client.patch(
        "/api/v1/settings",
        headers=headers,
        json={"auto_cleanup_days": "1"},
    )
    assert cleanup_response.status_code == 400

    theme_response = await client.patch(
        "/api/v1/settings",
        headers=headers,
        json={"theme": "blue"},
    )
    assert theme_response.status_code == 400


@pytest.mark.asyncio
async def test_settings_default_board_must_be_owned(client: AsyncClient):
    first_headers = await register(client, "First User", "first-settings@example.com")
    second_headers = await register(client, "Second User", "second-settings@example.com")

    boards_response = await client.get("/api/v1/boards", headers=second_headers)
    foreign_board_id = boards_response.json()["data"][0]["id"]

    response = await client.patch(
        "/api/v1/settings",
        headers=first_headers,
        json={"default_board_id": foreign_board_id},
    )
    assert response.status_code == 404
