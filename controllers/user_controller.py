from ticketing_system.schemas.user_schema import UserCreate
from ticketing_system.services.user_service import UserService

class UserController:
    def __init__(self):
        self.userService = UserService()

    def create_user(self, user: UserCreate):
        self.userService.create_user(user)
        return user
