from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


class ChecklistItem(Base):
    """
    Represents a checklist item (sub-task) within a card.
    Each card can have multiple checklist items that can be toggled.
    """
    __tablename__ = "checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(500), nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    position = Column(Integer, default=0, nullable=False)  # Order within card
    card_id = Column(Integer, ForeignKey("todos.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    card = relationship("Todo", backref="checklist_items")

    @staticmethod
    def get_by_id(db, item_id: int):
        return db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()

    @staticmethod
    def get_by_card(db, card_id: int):
        """Get all checklist items for a card, ordered by position."""
        return db.query(ChecklistItem).filter(
            ChecklistItem.card_id == card_id
        ).order_by(ChecklistItem.position).all()

    @staticmethod
    def get_max_position(db, card_id: int) -> int:
        """Get the highest position value in the card."""
        result = db.query(func.max(ChecklistItem.position)).filter(
            ChecklistItem.card_id == card_id
        ).scalar()
        return result if result is not None else -1

    @staticmethod
    def get_progress(db, card_id: int) -> dict:
        """Get checklist completion progress for a card."""
        items = ChecklistItem.get_by_card(db, card_id)
        total = len(items)
        completed = sum(1 for item in items if item.completed)
        return {
            "total": total,
            "completed": completed,
            "percentage": round((completed / total * 100) if total > 0 else 0, 1)
        }

    def save(self, db):
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db):
        db.delete(self)
        db.commit()

    def toggle(self, db):
        """Toggle the completed status."""
        self.completed = not self.completed
        return self.save(db)
