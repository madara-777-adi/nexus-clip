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


@pytest.mark.asyncio
async def test_delete_path_traversal(client: AsyncClient):
    """Path traversal payload in delete request is caught and silent fails."""
    import os
    import tempfile
    
    # Create a dummy file outside UPLOAD_DIR
    fd, dummy_path = tempfile.mkstemp()
    os.close(fd)
    try:
        # Write some data
        with open(dummy_path, "w") as f:
            f.write("secret data")
            
        # Attempt to delete the file using a path traversal payload
        # e.g., if UPLOAD_DIR is /tmp/nexus_uploads, the payload tries to go up.
        # We need a relative path from UPLOAD_DIR to dummy_path
        from app.services.storage_service import UPLOAD_DIR
        import os.path
        rel_path = os.path.relpath(dummy_path, UPLOAD_DIR)
        
        # Replace os.sep with / for the URL
        payload = rel_path.replace(os.sep, "/")
        
        # Test the service directly, because the HTTP router (Starlette) will naturally
        # collapse ../ in URLs, masking the underlying vulnerability in the service.
        from app.services.storage_service import StorageService
        service = StorageService()
        
        # This shouldn't raise an exception (silent fail)
        await service.delete_file(f"/static/uploads/{payload}")
        
        # ASSERT: The file outside UPLOAD_DIR was NOT deleted
        assert os.path.exists(dummy_path)
    finally:
        if os.path.exists(dummy_path):
            os.remove(dummy_path)


@pytest.mark.asyncio
async def test_delete_legitimate_file(client: AsyncClient):
    """Deleting a legitimate file inside UPLOAD_DIR succeeds and removes the file."""
    import os
    from app.services.storage_service import UPLOAD_DIR
    
    # Create a legitimate file
    filename = "legit_test_file.txt"
    file_path = UPLOAD_DIR / filename
    file_path.write_text("legit content")
    
    assert file_path.exists()
    
    response = await client.delete(f"/api/v1/upload/{filename}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    # ASSERT: The legitimate file WAS deleted
    assert not file_path.exists()
