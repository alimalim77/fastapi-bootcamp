from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CardCreate(BaseModel):
    """Schema for creating a new card/todo."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    due_date: Optional[datetime] = None
    position: Optional[int] = None  # Auto-calculated if not provided


class CardUpdate(BaseModel):
    """Schema for updating a card."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[Priority] = None
    due_date: Optional[datetime] = None


class CardMove(BaseModel):
    """Schema for moving a card to a different list/position."""
    list_id: Optional[int] = None  # Move to different list
    position: int = Field(..., ge=0)  # New position within list


class CardMemberResponse(BaseModel):
    """Schema for card member response."""
    user_id: int
    email: str
    assigned_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CardResponse(BaseModel):
    """Schema for card response."""
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    priority: Priority
    position: int
    due_date: Optional[datetime] = None
    list_id: Optional[int] = None
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CardDetailResponse(CardResponse):
    """Schema for detailed card response with members and labels."""
    members: List[CardMemberResponse] = []
    labels: List[dict] = []  # Will be LabelResponse


# Keep legacy aliases for backwards compatibility
TodoCreate = CardCreate
TodoUpdate = CardUpdate
TodoResponse = CardResponse
