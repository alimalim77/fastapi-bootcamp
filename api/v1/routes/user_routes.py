from fastapi import APIRouter
from ticketing_system.controllers.user_controller import UserController
from ticketing_system.schemas.user_schema import UserCreate, UserResponse

router = APIRouter()
controller = UserController()

@router.post("/register", response_model=UserCreate) 
def register_user(user: UserCreate):
    response = controller.create_user(user)
    return response

@router.get("/{user_id}",  response_model=UserResponse)
def get_user(user_id: int):
    return {
        "id": 12,
        "name" : "ALYM",
        'email' : "alimalim77@gmail.com"    
    }
