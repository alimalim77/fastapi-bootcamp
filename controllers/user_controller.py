from fastapi import HTTPException
from services.user_service import UserService
from schemas.user_schema import UserCreate, UserResponse, UserLogin, Token
from utils.jwt_handler import create_access_token, get_refresh_token_expiry
from models.refresh_token import RefreshToken
from datetime import timedelta, datetime, timezone
from utils.exceptions import UserAlreadyExistsError, UserNotFoundError


class UserController:
    def __init__(self):
        self.userService: UserService = UserService()

    def create_user(self, user: UserCreate, db) -> UserResponse:
        try:
            return self.userService.create_user(user, db)
        except UserAlreadyExistsError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_user_by_id(self, user_id: int, db):
        try:
            return self.userService.get_user_by_id(user_id, db)
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

    def login_user(self, user: UserLogin, db) -> Token:
        user_auth = self.userService.authenticate_user(user.email, user.password, db)
        if not user_auth:
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user_auth.email, "user_id": user_auth.id, "role": user_auth.role or "user"},
            expires_delta=access_token_expires
        )
        
        # Create refresh token
        refresh_token = RefreshToken(
            token=RefreshToken.generate_token(),
            user_id=user_auth.id,
            expires_at=get_refresh_token_expiry()
        )
        refresh_token.save(db)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token.token,
            "token_type": "bearer"
        }

    def refresh_access_token(self, refresh_token_str: str, db) -> dict:
        """Exchange a refresh token for a new access token."""
        # Find the refresh token
        token_record = RefreshToken.get_by_token(db, refresh_token_str)
        if not token_record:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Check if expired - handle both timezone-aware and naive datetimes
        expires_at = token_record.expires_at
        now = datetime.now(timezone.utc)
        
        # If expires_at is timezone-naive, assume it's UTC
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        if expires_at < now:
            token_record.revoke(db)
            raise HTTPException(status_code=401, detail="Refresh token expired")
        
        # Get the user
        user = self.userService.get_user_by_id(token_record.user_id, db)
        
        # Create new access token
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id, "role": user.role or "user"},
            expires_delta=timedelta(minutes=30)
        )
        
        return {"access_token": access_token, "token_type": "bearer"}

    def logout_user(self, refresh_token_str: str, db) -> dict:
        """Revoke a refresh token (logout)."""
        token_record = RefreshToken.get_by_token(db, refresh_token_str)
        if token_record:
            token_record.revoke(db)
        return {"message": "Successfully logged out"}