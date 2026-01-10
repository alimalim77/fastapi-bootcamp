from sqlalchemy import Column, Integer, String
from db.database import Base, SessionLocal

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    def save(self):
        db = SessionLocal()
        db.add(self)
        db.commit()
        db.refresh(self)
        db.close()
        return self

    @staticmethod
    def get_by_id(user_id: int):
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        db.close()
        return user
