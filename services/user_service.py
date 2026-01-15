from models.user_model import User
from schemas.user_schema import UserCreate
from utils.hash_generator import hash_password, verify_password
from utils.exceptions import UserAlreadyExistsError, UserNotFoundError # Import custom exceptions
class UserService:
    def create_user(self, payload: UserCreate, db):

        existing_user = User.get_by_email(db, payload.email)
        print(existing_user)
        if existing_user:
            raise UserAlreadyExistsError(f"User with email {payload.email} already exists")

        hashed_password = hash_password(payload.password)
        user = User(
            email=payload.email,
            password=hashed_password
        )
        saved_user = user.save(db)
        return saved_user
    
    def get_user_by_id(self, user_id: int, db):
        user = User.get_by_id(db, user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return user
    
    def authenticate_user(self, email: str, password: str, db):
        user = User.get_by_email(db, email)
        if not user:
            return False
        if not verify_password(password, user.password):
            return False
        return user