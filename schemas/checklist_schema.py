from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChecklistItemCreate(BaseModel):
    """Schema for creating a new checklist item."""
    content: str = Field(..., min_length=1, max_length=500)
    position: Optional[int] = None  # Auto-calculated if not provided


class ChecklistItemUpdate(BaseModel):
    """Schema for updating a checklist item."""
    content: Optional[str] = Field(None, min_length=1, max_length=500)
    completed: Optional[bool] = None


class ChecklistItemResponse(BaseModel):
    """Schema for checklist item response."""
    id: int
    content: str
    completed: bool
    position: int
    card_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChecklistProgressResponse(BaseModel):
    """Schema for checklist progress response."""
    total: int
    completed: int
    percentage: float
    items: List[ChecklistItemResponse] = []
