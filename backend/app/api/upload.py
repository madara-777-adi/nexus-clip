from fastapi import APIRouter, File, UploadFile, status

from app.schemas.response import APIResponse
from app.services.storage_service import StorageService

router = APIRouter(
    prefix="/upload",
    tags=["upload"],
)


@router.post(
    "",
    response_model=APIResponse[dict],
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    file: UploadFile = File(...),
) -> APIResponse[dict]:
    """Upload a file to storage (images, documents, code, etc.)."""
    service = StorageService()
    metadata = await service.save_file(file)
    return APIResponse(
        success=True,
        message="File uploaded successfully.",
        data=metadata,
    )


@router.delete(
    "/{file_name}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
)
async def delete_file(
    file_name: str,
) -> APIResponse[None]:
    """Delete an uploaded file."""
    service = StorageService()
    file_url = f"/static/uploads/{file_name}"
    await service.delete_file(file_url)
    return APIResponse(
        success=True,
        message="File deleted successfully.",
        data=None,
    )
