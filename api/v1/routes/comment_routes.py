from fastapi import APIRouter, Depends, Request, HTTPException
from controllers.comment_controller import CommentController
from schemas.comment_schema import (
    CommentCreate, CommentUpdate, CommentResponse, CommentListResponse
)
from db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()
controller = CommentController()


def get_current_user_id(request: Request) -> int:
    """Extract user_id from JWT payload stored in request.state by middleware."""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing user_id. Please login again.")
    return user_id


# Card-scoped routes
@router.post("/cards/{card_id}/comments", response_model=CommentResponse, status_code=201)
def create_comment(
    card_id: int,
    comment_data: CommentCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new comment on a card."""
    user_id = get_current_user_id(request)
    return controller.create_comment(card_id, user_id, comment_data, db)


@router.get("/cards/{card_id}/comments", response_model=CommentListResponse)
def get_card_comments(
    card_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get all comments for a card."""
    user_id = get_current_user_id(request)
    return controller.get_comments(card_id, user_id, db)


# Comment-scoped routes
@router.get("/comments/{comment_id}", response_model=CommentResponse)
def get_comment(
    comment_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get a specific comment."""
    user_id = get_current_user_id(request)
    return controller.get_comment(comment_id, user_id, db)


@router.put("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a comment (author-only)."""
    user_id = get_current_user_id(request)
    return controller.update_comment(comment_id, user_id, comment_data, db)


@router.delete("/comments/{comment_id}", status_code=204)
def delete_comment(
    comment_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a comment (author-only)."""
    user_id = get_current_user_id(request)
    controller.delete_comment(comment_id, user_id, db)
    return None
