from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LabelCreate(BaseModel):
    """Schema for creating a new label."""
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")  # Hex color


class LabelUpdate(BaseModel):
    """Schema for updating a label."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class LabelResponse(BaseModel):
    """Schema for label response."""
    id: int
    name: str
    color: str
    board_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CardLabelAttach(BaseModel):
    """Schema for attaching a label to a card."""
    label_id: int
