from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class BoardRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


# Board Schemas
class BoardCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field("#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$")


class BoardUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class BoardMemberResponse(BaseModel):
    user_id: int
    email: str
    role: BoardRole
    joined_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BoardResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    color: str
    owner_id: int
    created_at: Optional[datetime] = None
    member_count: int = 0

    class Config:
        from_attributes = True


class BoardDetailResponse(BoardResponse):
    members: List[BoardMemberResponse] = []


# Board Member Schemas
class BoardMemberAdd(BaseModel):
    user_id: int
    role: BoardRole = BoardRole.MEMBER


class BoardMemberUpdate(BaseModel):
    role: BoardRole
