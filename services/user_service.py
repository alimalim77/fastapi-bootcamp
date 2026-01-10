from fastapi import HTTPException
from models.user_model import User
from schemas.user_schema import UserCreate
from utils.hash_generator import hash_password

class UserService:
    def create_user(self, payload: UserCreate):
        try:
            hashed_password = hash_password(payload.password)
            user = User(
                email=payload.email,
                password=hashed_password
            )
            saved_user = user.save()
            return saved_user
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_user_by_id(self, user_id: int):
        user = User.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
