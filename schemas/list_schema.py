from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ListCreate(BaseModel):
    """Schema for creating a new list."""
    name: str = Field(..., min_length=1, max_length=100)
    position: Optional[int] = None  # Auto-calculated if not provided


class ListUpdate(BaseModel):
    """Schema for updating a list."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class ListMove(BaseModel):
    """Schema for moving/reordering a list."""
    position: int = Field(..., ge=0)


class ListResponse(BaseModel):
    """Schema for list response."""
    id: int
    name: str
    position: int
    board_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ListWithCardsResponse(ListResponse):
    """Schema for list response with cards included."""
    cards: list = []  # Will be populated with CardResponse in Phase 4
