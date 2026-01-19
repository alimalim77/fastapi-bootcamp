from fastapi import APIRouter, Depends, HTTPException
from controllers.user_controller import UserController
from schemas.user_schema import UserCreate, UserResponse, UserLogin, Token, RefreshTokenRequest
from middlewares.auth_validate import UserValidationSchema
from db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()
controller = UserController()


@router.post(
    "/register",
    response_model=UserResponse,
    summary="Register a new user",
    description="Create a new user account with email and password."
)
def register_user(user: UserValidationSchema, db: Session = Depends(get_db)):
    """Register a new user."""
    user_create = UserCreate(email=user.email, password=user.password)
    return controller.create_user(user_create, db)


@router.post(
    "/login",
    response_model=Token,
    summary="Login and get tokens",
    description="Authenticate with email and password to receive access and refresh tokens."
)
def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
    """Login and get access + refresh tokens."""
    return controller.login_user(form_data, db)


@router.post(
    "/refresh",
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access token."
)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Get a new access token using a refresh token."""
    return controller.refresh_access_token(request.refresh_token, db)


@router.post(
    "/logout",
    summary="Logout and revoke refresh token",
    description="Revoke the refresh token to logout."
)
def logout(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Logout by revoking the refresh token."""
    return controller.logout_user(request.refresh_token, db)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID"
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user details by ID."""
    user = controller.get_user_by_id(user_id, db)
    return {"id": user.id, "email": user.email}
