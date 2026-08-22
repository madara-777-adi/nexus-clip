import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_clips(client: AsyncClient):
    # Register user
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Search User",
            "email": "search@example.com",
            "password": "password123",
        },
    )
    headers = {"Authorization": f"Bearer {reg.json()['data']['access_token']}"}

    boards_res = await client.get("/api/v1/boards", headers=headers)
    board_id = boards_res.json()["data"][0]["id"]

    # Create clips
    await client.post(
        f"/api/v1/boards/{board_id}/clips",
        headers=headers,
        json={
            "type": "code",
            "title": "JWT Middleware",
            "content": "def jwt_verify(token): return True",
            "tags": ["python", "jwt"],
        },
    )
    await client.post(
        f"/api/v1/boards/{board_id}/clips",
        headers=headers,
        json={
            "type": "text",
            "title": "Shopping List",
            "content": "Buy milk, eggs, bread",
            "tags": ["personal"],
        },
    )

    # Search for "JWT"
    search_res = await client.get(
        "/api/v1/search?q=JWT",
        headers=headers,
    )
    assert search_res.status_code == 200
    items = search_res.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["title"] == "JWT Middleware"

    # Filter by type "code"
    code_res = await client.get(
        "/api/v1/search?type=code",
        headers=headers,
    )
    assert code_res.status_code == 200
    assert len(code_res.json()["data"]["items"]) == 1
