from app.schemas.auth import (
    GoogleLoginRequest,
    TokenResponse,
    UserLoginRequest,
    UserProfileResponse,
    UserRegisterRequest,
)
from app.schemas.board import BoardResponse, CreateBoardRequest, UpdateBoardRequest
from app.schemas.clip import (
    ClipListResponse,
    ClipResponse,
    CreateClipRequest,
    UpdateClipRequest,
)
from app.schemas.guest import (
    GuestBoardResponse,
    GuestContinueRequest,
    GuestPromoteResponse,
)
from app.schemas.response import APIResponse, ErrorResponse
from app.schemas.settings import UpdateSettingsRequest, UserSettingsResponse

__all__ = [
    "APIResponse",
    "ErrorResponse",
    "UserRegisterRequest",
    "UserLoginRequest",
    "GoogleLoginRequest",
    "UserProfileResponse",
    "TokenResponse",
    "CreateBoardRequest",
    "UpdateBoardRequest",
    "BoardResponse",
    "CreateClipRequest",
    "UpdateClipRequest",
    "ClipResponse",
    "ClipListResponse",
    "GuestBoardResponse",
    "GuestContinueRequest",
    "GuestPromoteResponse",
    "UserSettingsResponse",
    "UpdateSettingsRequest",
]
