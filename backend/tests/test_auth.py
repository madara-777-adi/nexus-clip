import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    # Register user
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "securepassword123",
        },
    )
    assert reg_response.status_code == 201
    data = reg_response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    token = data["data"]["access_token"]
    assert data["data"]["user"]["email"] == "testuser@example.com"

    # Profile (/me)
    me_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["data"]["email"] == "testuser@example.com"

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "securepassword123",
        },
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data["success"] is True
    assert "access_token" in login_data["data"]


@pytest.mark.asyncio
async def test_duplicate_registration_fails(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={
            "name": "User One",
            "email": "duplicate@example.com",
            "password": "password123",
        },
    )
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "User Two",
            "email": "duplicate@example.com",
            "password": "password456",
        },
    )
    assert resp.status_code == 409
    data = resp.json()
    assert data["success"] is False
