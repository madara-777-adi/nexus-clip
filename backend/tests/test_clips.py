import pytest
from httpx import AsyncClient


@pytest.fixture
async def setup_user_and_board(client: AsyncClient):
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Clip User",
            "email": "clips@example.com",
            "password": "password123",
        },
    )
    token = reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    boards_res = await client.get("/api/v1/boards", headers=headers)
    board_id = boards_res.json()["data"][0]["id"]
    return headers, board_id


@pytest.mark.asyncio
async def test_clip_lifecycle_and_pinning(client: AsyncClient, setup_user_and_board):
    headers, board_id = setup_user_and_board

    # 1. Create a text clip
    create_res = await client.post(
        f"/api/v1/boards/{board_id}/clips",
        headers=headers,
        json={
            "type": "text",
            "title": "Meeting Notes",
            "content": "Discuss V1 architecture",
            "tags": ["work", "meeting"],
        },
    )
    assert create_res.status_code == 201
    clip_data = create_res.json()["data"]
    clip_id = clip_data["id"]
    assert clip_data["title"] == "Meeting Notes"
    assert clip_data["is_pinned"] is False
    assert clip_data["tags"] == ["work", "meeting"]

    # 2. Toggle pin state
    pin_res = await client.patch(
        f"/api/v1/clips/{clip_id}/pin",
        headers=headers,
    )
    assert pin_res.status_code == 200
    assert pin_res.json()["data"]["is_pinned"] is True

    # 3. List clips in board (pinned clip should appear first)
    list_res = await client.get(
        f"/api/v1/boards/{board_id}/clips",
        headers=headers,
    )
    assert list_res.status_code == 200
    items = list_res.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["id"] == clip_id

    # 4. Delete clip
    del_res = await client.delete(
        f"/api/v1/clips/{clip_id}",
        headers=headers,
    )
    assert del_res.status_code == 200
