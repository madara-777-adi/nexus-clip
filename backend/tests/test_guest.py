import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_guest_session_and_clip_flow(client: AsyncClient):
    # 1. Initialize guest session
    init_res = await client.post("/api/v1/guest/board")
    assert init_res.status_code == 200
    session_data = init_res.json()["data"]
    session_id = session_data["guest_session_id"]
    # Board code must be None initially before first clip per PRODUCT_SPEC.md §4
    assert session_data["board_code"] is None

    # 2. Add first clip to guest board
    clip_res = await client.post(
        "/api/v1/guest/board/clips",
        headers={"x-guest-session-id": session_id},
        json={
            "type": "text",
            "title": "Guest Note",
            "content": "Temporary guest clipboard text",
        },
    )
    assert clip_res.status_code == 201
    clip_data = clip_res.json()["data"]
    assert clip_data["title"] == "Guest Note"

    # 3. Retrieve guest session again -> board code should now be visible!
    get_res = await client.post(
        "/api/v1/guest/board",
        headers={"x-guest-session-id": session_id},
    )
    assert get_res.status_code == 200
    session_data = get_res.json()["data"]
    board_code = session_data["board_code"]
    assert board_code is not None
    assert board_code.startswith("NEXUS-")

    # 4. Continue guest board on another device using board code
    cont_res = await client.post(
        "/api/v1/guest/continue",
        json={"boardCode": board_code},
    )
    assert cont_res.status_code == 200
    cont_data = cont_res.json()["data"]
    assert cont_data["guest_session_id"] == session_id
    assert len(cont_data["clips"]) == 1

    # 5. Promote guest board to authenticated user board
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Promoted User",
            "email": "promoted@example.com",
            "password": "password123",
        },
    )
    token = reg_res.json()["data"]["access_token"]

    promote_res = await client.post(
        "/api/v1/guest/promote",
        headers={
            "x-guest-session-id": session_id,
            "Authorization": f"Bearer {token}",
        },
    )
    assert promote_res.status_code == 200
    p_data = promote_res.json()["data"]
    assert p_data["moved_clips_count"] == 1
