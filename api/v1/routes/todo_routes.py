from fastapi import APIRouter, Depends, Request, HTTPException
from controllers.todo_controller import TodoController
from schemas.todo_schema import TodoCreate, TodoUpdate, TodoResponse
from db.session import get_db
from sqlalchemy.orm import Session
from typing import List
from middlewares.role_checker import RoleChecker

router = APIRouter()
controller = TodoController()


def get_current_user_id(request: Request) -> int:
    """Extract user_id from JWT payload stored in request.state by middleware."""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    user_id = user.get("user_id")
    if user_id:
        return user_id
    
    # Fallback: If token only has email (sub), fetch user from DB
    email = user.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")
        
    # We need a DB session here to query by email. 
    # But this function is a helper, not a dependency that gets DB.
    # Refactor: Make this a dependency `get_current_user` that returns the User object.
    # But for now, to keep changes minimal and fix the immediate int parsing error:
    # raising error if user_id is missing might be safest since we just updated the login controller.
    # The user has to re-login.
    raise HTTPException(status_code=401, detail="Token missing user_id. Please login again.")


@router.post("/", response_model=TodoResponse)
def create_todo(
    todo: TodoCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = get_current_user_id(request)
    return controller.create_todo(user_id, todo, db)


@router.get("/", response_model=List[TodoResponse])
def get_todos(
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = get_current_user_id(request)
    return controller.get_todos(user_id, db)


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    return controller.get_todo(todo_id, db)


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int,
    todo: TodoUpdate,
    db: Session = Depends(get_db)
):
    return controller.update_todo(todo_id, todo, db)


@router.delete("/{todo_id}", status_code=204, dependencies=[Depends(RoleChecker(["admin"]))])
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    """Delete a todo. Admin only."""
    controller.delete_todo(todo_id, db)
    return None
