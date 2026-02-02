from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


class Label(Base):
    """
    Represents a color-coded label/tag for cards within a board.
    Labels are board-scoped and can be attached to multiple cards.
    """
    __tablename__ = "labels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    color = Column(String(7), nullable=False)  # Hex color like #FF5733
    board_id = Column(Integer, ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    board = relationship("Board", backref="labels")
    # cards = relationship("Card", secondary="card_labels", back_populates="labels")  # Phase 4

    @staticmethod
    def get_by_id(db, label_id: int):
        return db.query(Label).filter(Label.id == label_id).first()

    @staticmethod
    def get_by_board(db, board_id: int):
        """Get all labels for a board."""
        return db.query(Label).filter(Label.board_id == board_id).all()

    def save(self, db):
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db):
        db.delete(self)
        db.commit()


class CardLabel(Base):
    """
    Junction table for many-to-many relationship between Cards and Labels.
    Used in Phase 4 when Cards are implemented.
    """
    __tablename__ = "card_labels"

    card_id = Column(Integer, ForeignKey("todos.id", ondelete="CASCADE"), primary_key=True)
    label_id = Column(Integer, ForeignKey("labels.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @staticmethod
    def get_card_labels(db, card_id: int):
        """Get all labels attached to a card."""
        return db.query(CardLabel).filter(CardLabel.card_id == card_id).all()

    @staticmethod
    def attach(db, card_id: int, label_id: int):
        """Attach a label to a card."""
        card_label = CardLabel(card_id=card_id, label_id=label_id)
        db.add(card_label)
        db.commit()
        return card_label

    @staticmethod
    def detach(db, card_id: int, label_id: int):
        """Detach a label from a card."""
        card_label = db.query(CardLabel).filter(
            CardLabel.card_id == card_id,
            CardLabel.label_id == label_id
        ).first()
        if card_label:
            db.delete(card_label)
            db.commit()
            return True
        return False
