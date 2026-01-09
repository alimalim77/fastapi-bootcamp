from fastapi import HTTPException
from models.user_model import User
from schemas.user_schema import UserCreate

class UserService:
    def create_user(self, payload: UserCreate):
        user = User(
            name=payload.name,
            email=payload.email
        )
        user.save()
        return user

    def get_user_by_id(self, user_id: int):
        user = User.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
