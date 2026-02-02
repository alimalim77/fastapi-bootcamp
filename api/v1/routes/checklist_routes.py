from fastapi import APIRouter, Depends, Request, HTTPException
from controllers.checklist_controller import ChecklistController
from schemas.checklist_schema import (
    ChecklistItemCreate, ChecklistItemUpdate, ChecklistItemResponse, ChecklistProgressResponse
)
from db.session import get_db
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()
controller = ChecklistController()


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
@router.post("/cards/{card_id}/checklist", response_model=ChecklistItemResponse, status_code=201)
def create_checklist_item(
    card_id: int,
    item_data: ChecklistItemCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new checklist item in a card."""
    user_id = get_current_user_id(request)
    return controller.create_item(card_id, user_id, item_data, db)


@router.get("/cards/{card_id}/checklist", response_model=List[ChecklistItemResponse])
def get_checklist_items(
    card_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get all checklist items for a card."""
    user_id = get_current_user_id(request)
    return controller.get_items(card_id, user_id, db)


@router.get("/cards/{card_id}/checklist/progress", response_model=ChecklistProgressResponse)
def get_checklist_progress(
    card_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get checklist completion progress for a card."""
    user_id = get_current_user_id(request)
    return controller.get_progress(card_id, user_id, db)


# Checklist item-scoped routes
@router.get("/checklist/{item_id}", response_model=ChecklistItemResponse)
def get_checklist_item(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get a specific checklist item."""
    user_id = get_current_user_id(request)
    return controller.get_item(item_id, user_id, db)


@router.put("/checklist/{item_id}", response_model=ChecklistItemResponse)
def update_checklist_item(
    item_id: int,
    item_data: ChecklistItemUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a checklist item."""
    user_id = get_current_user_id(request)
    return controller.update_item(item_id, user_id, item_data, db)


@router.patch("/checklist/{item_id}/toggle", response_model=ChecklistItemResponse)
def toggle_checklist_item(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Toggle a checklist item's completed status."""
    user_id = get_current_user_id(request)
    return controller.toggle_item(item_id, user_id, db)


@router.delete("/checklist/{item_id}", status_code=204)
def delete_checklist_item(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a checklist item."""
    user_id = get_current_user_id(request)
    controller.delete_item(item_id, user_id, db)
    return None
