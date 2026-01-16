from fastapi import APIRouter, Depends, Request
from controllers.todo_controller import TodoController
from schemas.todo_schema import TodoCreate, TodoUpdate, TodoResponse
from db.session import get_db
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()
controller = TodoController()


def get_current_user_id(request: Request) -> int:
    """Extract user_id from JWT payload stored in request.state by middleware."""
    user = getattr(request.state, "user", None)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="User not authenticated")
    # Assuming the JWT payload has 'sub' as email, we need user_id
    # For now, we'll extract it from the token payload
    # You may need to adjust based on your JWT structure
    return user.get("user_id") or user.get("sub")


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


@router.delete("/{todo_id}", status_code=204)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    controller.delete_todo(todo_id, db)
    return None
