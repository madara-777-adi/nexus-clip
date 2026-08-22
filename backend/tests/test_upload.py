import io

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_file_upload_allowed_extension(client: AsyncClient):
    """Allowed extensions (.js) upload successfully."""
    file_content = b"console.log('Nexus Clip upload test');"
    files = {"file": ("test_script.js", io.BytesIO(file_content), "application/javascript")}

    response = await client.post("/api/v1/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    meta = data["data"]
    assert meta["file_name"] == "test_script.js"
    assert "file_url" in meta


@pytest.mark.asyncio
async def test_file_upload_blocked_html(client: AsyncClient):
    """HTML files are rejected with 400 ValidationError."""
    file_content = b"<html><script>alert(1)</script></html>"
    files = {"file": ("evil.html", io.BytesIO(file_content), "text/html")}

    response = await client.post("/api/v1/upload", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert ".html" in data["message"] or "not allowed" in data["message"]


@pytest.mark.asyncio
async def test_file_upload_blocked_svg(client: AsyncClient):
    """SVG files are rejected with 400 ValidationError."""
    file_content = b"<svg><script>alert(1)</script></svg>"
    files = {"file": ("evil.svg", io.BytesIO(file_content), "image/svg+xml")}

    response = await client.post("/api/v1/upload", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False


@pytest.mark.asyncio
async def test_file_upload_too_large(client: AsyncClient, monkeypatch):
    """Files exceeding MAX_UPLOAD_SIZE_MB are rejected with 413."""
    from app.core import config as cfg

    # Temporarily lower the limit to 1 byte so we don't allocate 25 MB in CI
    monkeypatch.setattr(cfg.settings, "max_upload_size_mb", 0)

    file_content = b"x" * 1025  # 1 KB > 0 MB limit
    files = {"file": ("big.txt", io.BytesIO(file_content), "text/plain")}

    response = await client.post("/api/v1/upload", files=files)
    assert response.status_code == 413
    data = response.json()
    assert data["success"] is False
