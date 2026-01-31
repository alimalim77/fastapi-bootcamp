from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base
import enum


class BoardRole(enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"


class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    color = Column(String(7), default="#3B82F6")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    owner = relationship("User", backref="owned_boards", foreign_keys=[owner_id])
    members = relationship("BoardMember", back_populates="board", cascade="all, delete-orphan")
    # lists = relationship("List", back_populates="board", cascade="all, delete-orphan")  # Phase 2
    # labels = relationship("Label", back_populates="board", cascade="all, delete-orphan")  # Phase 3

    @staticmethod
    def get_by_id(db, board_id: int):
        return db.query(Board).filter(Board.id == board_id).first()

    @staticmethod
    def get_by_user(db, user_id: int):
        """Get all boards where user is owner or member"""
        from models.board import BoardMember
        owned = db.query(Board).filter(Board.owner_id == user_id).all()
        member_boards = db.query(Board).join(BoardMember).filter(
            BoardMember.user_id == user_id
        ).all()
        # Combine and deduplicate
        all_boards = {b.id: b for b in owned + member_boards}
        return list(all_boards.values())

    def save(self, db):
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db):
        db.delete(self)
        db.commit()


class BoardMember(Base):
    __tablename__ = "board_members"

    board_id = Column(Integer, ForeignKey("boards.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role = Column(Enum(BoardRole), default=BoardRole.MEMBER, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    board = relationship("Board", back_populates="members")
    user = relationship("User", backref="board_memberships")

    @staticmethod
    def get_membership(db, board_id: int, user_id: int):
        return db.query(BoardMember).filter(
            BoardMember.board_id == board_id,
            BoardMember.user_id == user_id
        ).first()

    def save(self, db):
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db):
        db.delete(self)
        db.commit()
