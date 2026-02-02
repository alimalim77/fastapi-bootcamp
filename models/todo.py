from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base
import enum


class Priority(enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Todo(Base):
    """
    Card/Todo model - represents a task within a list.
    Enhanced with list positioning and due dates for Kanban functionality.
    """
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(Enum(Priority), default=Priority.MEDIUM, nullable=False)
    position = Column(Integer, default=0, nullable=False)  # Order within list
    due_date = Column(DateTime(timezone=True), nullable=True)  # Deadline
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Creator/author
    list_id = Column(Integer, ForeignKey("lists.id", ondelete="SET NULL"), nullable=True)  # Parent list
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="todos")
    list = relationship("List", backref="cards")
    members = relationship("CardMember", back_populates="card", cascade="all, delete-orphan")
    labels = relationship("Label", secondary="card_labels", backref="cards")

    @staticmethod
    def get_by_id(db, todo_id: int):
        return db.query(Todo).filter(Todo.id == todo_id).first()

    @staticmethod
    def get_by_user(db, user_id: int):
        return db.query(Todo).filter(Todo.user_id == user_id).all()

    @staticmethod
    def get_by_list(db, list_id: int):
        """Get all cards in a list, ordered by position."""
        return db.query(Todo).filter(Todo.list_id == list_id).order_by(Todo.position).all()

    @staticmethod
    def get_max_position(db, list_id: int) -> int:
        """Get the highest position value in the list."""
        result = db.query(func.max(Todo.position)).filter(Todo.list_id == list_id).scalar()
        return result if result is not None else -1

    def save(self, db):
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db):
        db.delete(self)
        db.commit()


class CardMember(Base):
    """
    Junction table for many-to-many relationship between Cards and Users (assignees).
    """
    __tablename__ = "card_members"

    card_id = Column(Integer, ForeignKey("todos.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    card = relationship("Todo", back_populates="members")
    user = relationship("User", backref="card_assignments")

    @staticmethod
    def get_card_members(db, card_id: int):
        """Get all members assigned to a card."""
        return db.query(CardMember).filter(CardMember.card_id == card_id).all()

    @staticmethod
    def assign(db, card_id: int, user_id: int):
        """Assign a user to a card."""
        member = CardMember(card_id=card_id, user_id=user_id)
        db.add(member)
        db.commit()
        return member

    @staticmethod
    def unassign(db, card_id: int, user_id: int):
        """Unassign a user from a card."""
        member = db.query(CardMember).filter(
            CardMember.card_id == card_id,
            CardMember.user_id == user_id
        ).first()
        if member:
            db.delete(member)
            db.commit()
            return True
        return False
