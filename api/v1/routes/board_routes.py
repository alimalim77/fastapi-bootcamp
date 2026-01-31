from fastapi import APIRouter, Depends, Request, HTTPException
from controllers.board_controller import BoardController
from schemas.board_schema import (
    BoardCreate, BoardUpdate, BoardResponse, BoardDetailResponse,
    BoardMemberAdd, BoardMemberResponse
)
from db.session import get_db
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()
controller = BoardController()


def get_current_user_id(request: Request) -> int:
    """Extract user_id from JWT payload stored in request.state by middleware."""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing user_id. Please login again.")
    return user_id


@router.post("/", response_model=BoardResponse, status_code=201)
def create_board(
    board: BoardCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new board. The creator becomes the owner and admin."""
    user_id = get_current_user_id(request)
    return controller.create_board(user_id, board, db)


@router.get("/", response_model=List[BoardResponse])
def get_boards(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get all boards where the user is an owner or member."""
    user_id = get_current_user_id(request)
    return controller.get_boards(user_id, db)


@router.get("/{board_id}", response_model=BoardDetailResponse)
def get_board(
    board_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get board details including members. Requires board access."""
    user_id = get_current_user_id(request)
    return controller.get_board(board_id, user_id, db)


@router.put("/{board_id}", response_model=BoardResponse)
def update_board(
    board_id: int,
    board: BoardUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a board. Admin only."""
    user_id = get_current_user_id(request)
    return controller.update_board(board_id, user_id, board, db)


@router.delete("/{board_id}", status_code=204)
def delete_board(
    board_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a board and all its contents. Owner only."""
    user_id = get_current_user_id(request)
    controller.delete_board(board_id, user_id, db)
    return None


# Member management endpoints
@router.post("/{board_id}/members", response_model=BoardMemberResponse, status_code=201)
def add_member(
    board_id: int,
    member: BoardMemberAdd,
    request: Request,
    db: Session = Depends(get_db)
):
    """Add a member to the board. Admin only."""
    user_id = get_current_user_id(request)
    return controller.add_member(board_id, user_id, member, db)


@router.delete("/{board_id}/members/{target_user_id}", status_code=204)
def remove_member(
    board_id: int,
    target_user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Remove a member from the board. Admin only. Cannot remove owner."""
    user_id = get_current_user_id(request)
    controller.remove_member(board_id, user_id, target_user_id, db)
    return None
