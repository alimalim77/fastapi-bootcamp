from fastapi import APIRouter, Depends, Request, HTTPException
from controllers.list_controller import ListController
from schemas.list_schema import (
    ListCreate, ListUpdate, ListMove, ListResponse
)
from db.session import get_db
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()
controller = ListController()


def get_current_user_id(request: Request) -> int:
    """Extract user_id from JWT payload stored in request.state by middleware."""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing user_id. Please login again.")
    return user_id


# Board-scoped routes
@router.post("/boards/{board_id}/lists", response_model=ListResponse, status_code=201)
def create_list(
    board_id: int,
    list_data: ListCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new list in a board. Position auto-calculated if not provided."""
    user_id = get_current_user_id(request)
    return controller.create_list(board_id, user_id, list_data, db)


@router.get("/boards/{board_id}/lists", response_model=List[ListResponse])
def get_lists(
    board_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get all lists for a board, ordered by position."""
    user_id = get_current_user_id(request)
    return controller.get_lists(board_id, user_id, db)


# List-scoped routes
@router.get("/lists/{list_id}", response_model=ListResponse)
def get_list(
    list_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get a specific list by ID."""
    user_id = get_current_user_id(request)
    return controller.get_list(list_id, user_id, db)


@router.put("/lists/{list_id}", response_model=ListResponse)
def update_list(
    list_id: int,
    list_data: ListUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a list's name."""
    user_id = get_current_user_id(request)
    return controller.update_list(list_id, user_id, list_data, db)


@router.patch("/lists/{list_id}/move", response_model=ListResponse)
def move_list(
    list_id: int,
    move_data: ListMove,
    request: Request,
    db: Session = Depends(get_db)
):
    """Move a list to a new position within the board."""
    user_id = get_current_user_id(request)
    return controller.move_list(list_id, user_id, move_data, db)


@router.delete("/lists/{list_id}", status_code=204)
def delete_list(
    list_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a list and all its cards."""
    user_id = get_current_user_id(request)
    controller.delete_list(list_id, user_id, db)
    return None
