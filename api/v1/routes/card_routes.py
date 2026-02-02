from fastapi import APIRouter, Depends, Request, HTTPException
from services.todo_service import CardService
from schemas.todo_schema import (
    CardCreate, CardUpdate, CardMove, CardResponse, CardDetailResponse, CardMemberResponse
)
from db.session import get_db
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()
service = CardService()


def get_current_user_id(request: Request) -> int:
    """Extract user_id from JWT payload stored in request.state by middleware."""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing user_id. Please login again.")
    return user_id


def _to_response(card) -> CardResponse:
    return CardResponse(
        id=card.id,
        title=card.title,
        description=card.description,
        completed=card.completed,
        priority=card.priority.value,
        position=card.position,
        due_date=card.due_date,
        list_id=card.list_id,
        user_id=card.user_id,
        created_at=card.created_at,
        updated_at=card.updated_at
    )


def _to_detail_response(card, db) -> CardDetailResponse:
    members = []
    for m in card.members:
        members.append(CardMemberResponse(
            user_id=m.user_id,
            email=m.user.email if m.user else "",
            assigned_at=m.assigned_at
        ))
    
    labels = []
    for lbl in card.labels:
        labels.append({
            "id": lbl.id,
            "name": lbl.name,
            "color": lbl.color
        })
    
    return CardDetailResponse(
        id=card.id,
        title=card.title,
        description=card.description,
        completed=card.completed,
        priority=card.priority.value,
        position=card.position,
        due_date=card.due_date,
        list_id=card.list_id,
        user_id=card.user_id,
        created_at=card.created_at,
        updated_at=card.updated_at,
        members=members,
        labels=labels
    )


# List-scoped routes
@router.post("/lists/{list_id}/cards", response_model=CardResponse, status_code=201)
def create_card(
    list_id: int,
    card_data: CardCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new card in a list. Position auto-calculated if not provided."""
    user_id = get_current_user_id(request)
    card = service.create_card(list_id, user_id, card_data, db)
    return _to_response(card)


@router.get("/lists/{list_id}/cards", response_model=List[CardResponse])
def get_cards(
    list_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get all cards in a list, ordered by position."""
    user_id = get_current_user_id(request)
    cards = service.get_cards_by_list(list_id, user_id, db)
    return [_to_response(c) for c in cards]


# Card-scoped routes
@router.get("/cards/{card_id}", response_model=CardDetailResponse)
def get_card(
    card_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get a specific card with members and labels."""
    user_id = get_current_user_id(request)
    card = service.get_card_by_id(card_id, user_id, db)
    return _to_detail_response(card, db)


@router.put("/cards/{card_id}", response_model=CardResponse)
def update_card(
    card_id: int,
    card_data: CardUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a card's fields."""
    user_id = get_current_user_id(request)
    card = service.update_card(card_id, user_id, card_data, db)
    return _to_response(card)


@router.patch("/cards/{card_id}/move", response_model=CardResponse)
def move_card(
    card_id: int,
    move_data: CardMove,
    request: Request,
    db: Session = Depends(get_db)
):
    """Move a card to a new position or different list."""
    user_id = get_current_user_id(request)
    card = service.move_card(card_id, user_id, move_data, db)
    return _to_response(card)


@router.delete("/cards/{card_id}", status_code=204)
def delete_card(
    card_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a card."""
    user_id = get_current_user_id(request)
    service.delete_card(card_id, user_id, db)
    return None


# Card member assignment routes
@router.post("/cards/{card_id}/members/{user_id}", status_code=201)
def assign_member(
    card_id: int,
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Assign a user to a card."""
    current_user_id = get_current_user_id(request)
    service.assign_member(card_id, user_id, current_user_id, db)
    return {"message": "User assigned successfully"}


@router.delete("/cards/{card_id}/members/{user_id}", status_code=204)
def unassign_member(
    card_id: int,
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Unassign a user from a card."""
    current_user_id = get_current_user_id(request)
    service.unassign_member(card_id, user_id, current_user_id, db)
    return None
