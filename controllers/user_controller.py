from services.user_service import UserService
from schemas.user_schema import UserCreate, UserResponse

class UserController:
    def __init__(self):
        self.userService = UserService()

    def create_user(self, user: UserCreate) -> UserResponse:
        # No try-except needed - Service handles it
        return self.userService.create_user(user)