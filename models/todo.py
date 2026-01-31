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
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(Enum(Priority), default=Priority.MEDIUM, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to User
    user = relationship("User", backref="todos")

    @staticmethod
    def get_by_id(db, todo_id: int):
        return db.query(Todo).filter(Todo.id == todo_id).first()

    @staticmethod
    def get_by_user(db, user_id: int):
        return db.query(Todo).filter(Todo.user_id == user_id).all()

    def save(self, db):
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db):
        db.delete(self)
        db.commit()
