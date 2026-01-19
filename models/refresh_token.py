from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from db.database import Base
import secrets


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @staticmethod
    def generate_token() -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(64)

    @staticmethod
    def get_by_token(db, token: str):
        return db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.revoked == False
        ).first()

    @staticmethod
    def revoke_all_for_user(db, user_id: int):
        """Revoke all refresh tokens for a user (useful for password change)."""
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id
        ).update({"revoked": True})
        db.commit()

    def save(self, db):
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def revoke(self, db):
        self.revoked = True
        db.commit()
