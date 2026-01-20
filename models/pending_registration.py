from sqlalchemy import Column, Integer, String, DateTime
from db.database import Base
from datetime import datetime, timezone, timedelta
import secrets
import hashlib


class PendingRegistration(Base):
    """Stores pending user registrations awaiting OTP verification."""
    __tablename__ = "pending_registrations"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    otp_hash = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    @staticmethod
    def generate_otp() -> str:
        """Generate a 6-digit OTP code."""
        return str(secrets.randbelow(900000) + 100000)

    @staticmethod
    def hash_otp(otp: str) -> str:
        """Hash OTP for secure storage."""
        return hashlib.sha256(otp.encode()).hexdigest()

    def verify_otp(self, otp: str) -> bool:
        """Verify if provided OTP matches stored hash."""
        return self.otp_hash == self.hash_otp(otp)

    def is_expired(self) -> bool:
        """Check if OTP has expired."""
        now = datetime.now(timezone.utc)
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return now > expires

    @staticmethod
    def get_expiry_time(minutes: int = 10) -> datetime:
        """Get expiration time for OTP (default 10 minutes)."""
        return datetime.now(timezone.utc) + timedelta(minutes=minutes)

    @staticmethod
    def get_by_id(db, registration_id: int) -> "PendingRegistration":
        return db.query(PendingRegistration).filter(
            PendingRegistration.id == registration_id
        ).first()

    @staticmethod
    def get_by_email(db, email: str) -> "PendingRegistration":
        return db.query(PendingRegistration).filter(
            PendingRegistration.email == email
        ).first()

    def save(self, db) -> "PendingRegistration":
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db) -> None:
        db.delete(self)
        db.commit()

    def update_otp(self, db, new_otp: str) -> "PendingRegistration":
        """Update OTP and expiry for resending."""
        self.otp_hash = self.hash_otp(new_otp)
        self.expires_at = self.get_expiry_time()
        db.commit()
        db.refresh(self)
        return self
