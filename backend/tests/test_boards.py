import pytest
from httpx import AsyncClient


@pytest.fixture
async def auth_headers(client: AsyncClient):
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Board User",
            "email": "boards@example.com",
            "password": "password123",
        },
    )
    token = reg.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_board_crud(client: AsyncClient, auth_headers: dict):
    # 1. List initial boards (default board should exist)
    list_res = await client.get("/api/v1/boards", headers=auth_headers)
    assert list_res.status_code == 200
    boards = list_res.json()["data"]
    assert len(boards) >= 1
    default_board = boards[0]
    assert default_board["is_default"] is True

    # 2. Create a new custom board
    create_res = await client.post(
        "/api/v1/boards",
        headers=auth_headers,
        json={"name": "Project Alpha"},
    )
    assert create_res.status_code == 201
    new_board = create_res.json()["data"]
    assert new_board["name"] == "Project Alpha"
    board_id = new_board["id"]

    # 3. Rename board
    patch_res = await client.patch(
        f"/api/v1/boards/{board_id}",
        headers=auth_headers,
        json={"name": "Project Alpha Updated"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["data"]["name"] == "Project Alpha Updated"

    # 4. Delete board
    del_res = await client.delete(
        f"/api/v1/boards/{board_id}",
        headers=auth_headers,
    )
    assert del_res.status_code == 200
