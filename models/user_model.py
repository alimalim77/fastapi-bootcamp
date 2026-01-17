from sqlalchemy import Column, Integer, String
from db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="user")

    @staticmethod
    def get_by_id(db, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db, email: str):
        return db.query(User).filter(User.email == email).first()
    
    def save(self, db):
        db.add(self)
        db.commit()
        db.refresh(self)
        return self