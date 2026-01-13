from fastapi import APIRouter, Depends
from controllers.user_controller import UserController
from schemas.user_schema import UserCreate, UserResponse
from middlewares.auth_validate import UserValidationSchema
from db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()
controller = UserController()

@router.post("/register") 
def register_user(user: UserValidationSchema,
                      db: Session = Depends(get_db)):
    response = controller.create_user(user, db)
    return response

@router.get("/{user_id}",  response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = controller.get_user_by_id(user_id, db)
    return {
        "id": user.id,
        'email' : user.email    
    }
