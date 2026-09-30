from fastapi import APIRouter, Depends, File, Header, Query, UploadFile, status

from app.api.dependencies import get_optional_current_user
from app.core.exceptions import UnauthorizedError
from app.models.user import User
from app.schemas.response import APIResponse
from app.storage.service import StorageService

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
    x_guest_session_id: str | None = Header(default=None),
    current_user: User | None = Depends(get_optional_current_user),
) -> APIResponse[dict]:
    """Upload a file for an authenticated user or active guest session."""
    if current_user is None and not x_guest_session_id:
        raise UnauthorizedError("Authentication or a guest session is required.")
    service = StorageService()
    metadata = await service.save_file(
        file,
        owner_id=str(current_user.id) if current_user else x_guest_session_id,
        owner_type="user" if current_user else "guest",
    )
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
    token: str = Query(...),
    x_guest_session_id: str | None = Header(default=None),
    current_user: User | None = Depends(get_optional_current_user),
) -> APIResponse[None]:
    """Delete an uploaded file owned by the authenticated user or guest session."""
    if current_user is None and not x_guest_session_id:
        raise UnauthorizedError("Authentication or a guest session is required.")
    service = StorageService()
    file_url = f"/static/uploads/{file_name}"
    await service.delete_file(
        file_url,
        token,
        owner_id=str(current_user.id) if current_user else x_guest_session_id,
        owner_type="user" if current_user else "guest",
    )
    return APIResponse(
        success=True,
        message="File deleted successfully.",
        data=None,
    )
