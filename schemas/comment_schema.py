from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CommentCreate(BaseModel):
    """Schema for creating a new comment."""
    content: str = Field(..., min_length=1, max_length=2000)


class CommentUpdate(BaseModel):
    """Schema for updating a comment (author-only)."""
    content: str = Field(..., min_length=1, max_length=2000)


class AuthorResponse(BaseModel):
    """Minimal author info for comment response."""
    id: int
    email: str

    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    """Schema for comment response."""
    id: int
    content: str
    card_id: int
    author_id: int
    author: Optional[AuthorResponse] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    """Schema for list of comments."""
    comments: List[CommentResponse]
    total: int
