from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


class List(Base):
    """
    Represents a Kanban column within a board (e.g., "To Do", "In Progress", "Done").
    Lists contain cards and are ordered by position.
    """
    __tablename__ = "lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    position = Column(Integer, default=0, nullable=False)
    board_id = Column(Integer, ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    board = relationship("Board", backref="lists")
    # cards = relationship("Card", back_populates="list", cascade="all, delete-orphan")  # Phase 4

    @staticmethod
    def get_by_id(db, list_id: int):
        return db.query(List).filter(List.id == list_id).first()

    @staticmethod
    def get_by_board(db, board_id: int):
        """Get all lists for a board, ordered by position."""
        return db.query(List).filter(List.board_id == board_id).order_by(List.position).all()

    @staticmethod
    def get_max_position(db, board_id: int) -> int:
        """Get the highest position value in the board."""
        result = db.query(func.max(List.position)).filter(List.board_id == board_id).scalar()
        return result if result is not None else -1

    def save(self, db):
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db):
        db.delete(self)
        db.commit()
