from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


class Comment(Base):
    """
    Represents a comment on a card.
    Only the author can edit/delete their own comments.
    All board members can view comments on cards they have access to.
    """
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(2000), nullable=False)
    card_id = Column(Integer, ForeignKey("todos.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    card = relationship("Todo", backref="comments")
    author = relationship("User", backref="comments")

    @staticmethod
    def get_by_id(db, comment_id: int):
        return db.query(Comment).filter(Comment.id == comment_id).first()

    @staticmethod
    def get_by_card(db, card_id: int):
        """Get all comments for a card, ordered by creation time."""
        return db.query(Comment).filter(
            Comment.card_id == card_id
        ).order_by(Comment.created_at.asc()).all()

    @staticmethod
    def get_by_author(db, author_id: int):
        """Get all comments by a specific author."""
        return db.query(Comment).filter(
            Comment.author_id == author_id
        ).order_by(Comment.created_at.desc()).all()

    def is_author(self, user_id: int) -> bool:
        """Check if user is the author of this comment."""
        return self.author_id == user_id

    def save(self, db):
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db):
        db.delete(self)
        db.commit()
