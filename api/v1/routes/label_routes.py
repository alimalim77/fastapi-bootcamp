from fastapi import APIRouter, Depends, Request, HTTPException
from controllers.label_controller import LabelController
from schemas.label_schema import LabelCreate, LabelUpdate, LabelResponse
from db.session import get_db
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()
controller = LabelController()


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
@router.post("/boards/{board_id}/labels", response_model=LabelResponse, status_code=201)
def create_label(
    board_id: int,
    label_data: LabelCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new label in a board."""
    user_id = get_current_user_id(request)
    return controller.create_label(board_id, user_id, label_data, db)


@router.get("/boards/{board_id}/labels", response_model=List[LabelResponse])
def get_labels(
    board_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get all labels for a board."""
    user_id = get_current_user_id(request)
    return controller.get_labels(board_id, user_id, db)


# Label-scoped routes
@router.get("/labels/{label_id}", response_model=LabelResponse)
def get_label(
    label_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get a specific label by ID."""
    user_id = get_current_user_id(request)
    return controller.get_label(label_id, user_id, db)


@router.put("/labels/{label_id}", response_model=LabelResponse)
def update_label(
    label_id: int,
    label_data: LabelUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a label's name or color."""
    user_id = get_current_user_id(request)
    return controller.update_label(label_id, user_id, label_data, db)


@router.delete("/labels/{label_id}", status_code=204)
def delete_label(
    label_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a label."""
    user_id = get_current_user_id(request)
    controller.delete_label(label_id, user_id, db)
    return None


# Card-Label attachment routes (for Phase 4 integration)
@router.post("/cards/{card_id}/labels/{label_id}", status_code=201)
def attach_label_to_card(
    card_id: int,
    label_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Attach a label to a card."""
    user_id = get_current_user_id(request)
    controller.attach_to_card(card_id, label_id, user_id, db)
    return {"message": "Label attached successfully"}


@router.delete("/cards/{card_id}/labels/{label_id}", status_code=204)
def detach_label_from_card(
    card_id: int,
    label_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Detach a label from a card."""
    user_id = get_current_user_id(request)
    controller.detach_from_card(card_id, label_id, user_id, db)
    return None
