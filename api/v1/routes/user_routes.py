from fastapi import APIRouter, Depends
from controllers.user_controller import UserController
from schemas.user_schema import UserCreate, UserResponse, UserLogin, Token
from middlewares.auth_validate import UserValidationSchema
from db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()
controller = UserController()

@router.post("/register", response_model=UserResponse) 
def register_user(user: UserValidationSchema,
                      db: Session = Depends(get_db)):
    user_create = UserCreate(email=user.email, password=user.password)
    response = controller.create_user(user_create, db)
    return response

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
    return controller.login_user(form_data, db)

@router.get("/{user_id}",  response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = controller.get_user_by_id(user_id, db)
    return {
        "id": user.id,
        'email' : user.email    
    }
