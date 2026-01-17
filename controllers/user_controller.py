from fastapi import HTTPException
from services.user_service import UserService
from schemas.user_schema import UserCreate, UserResponse, UserLogin, Token
from utils.jwt_handler import create_access_token
from datetime import timedelta
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
        
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user_auth.email, "user_id": user_auth.id, "role": user_auth.role or "user"}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}