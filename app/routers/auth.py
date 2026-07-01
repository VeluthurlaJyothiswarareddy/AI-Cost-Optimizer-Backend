from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database import get_revoked_tokens_collection, get_users_collection
from app.dependencies.auth import get_current_user
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    LogoutResponse,
    RegisterRequest,
    RegisterResponse,
    UserResponse,
)
from app.services.auth_service import AuthError, auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest) -> RegisterResponse:
    collection = get_users_collection()
    try:
        result = await auth_service.register(
            collection=collection,
            email=request.email,
            password=request.password,
        )
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc

    return RegisterResponse(
        message="Account created successfully. Please sign in.",
        user=UserResponse(**result["user"]),
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest) -> AuthResponse:
    collection = get_users_collection()
    try:
        result = await auth_service.login(
            collection=collection,
            email=request.email,
            password=request.password,
        )
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
        ) from exc

    return AuthResponse(
        access_token=result["access_token"],
        user=UserResponse(**result["user"]),
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    _: dict = Depends(get_current_user),
) -> LogoutResponse:
    revoked_collection = get_revoked_tokens_collection()
    await auth_service.revoke_token(revoked_collection, credentials.credentials)
    return LogoutResponse(message="Logged out successfully.")
