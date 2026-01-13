from services.user_service import UserService
from schemas.user_schema import UserCreate, UserResponse

class UserController:
    def __init__(self):
        self.userService = UserService()

    def create_user(self, user: UserCreate, db) -> UserResponse:
        # No try-except needed - Service handles it
        return self.userService.create_user(user, db)

    def get_user_by_id(self, user_id: int, db):
        return self.userService.get_user_by_id(user_id, db)