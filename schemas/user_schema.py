from fastapi import FastAPI 
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class RegisterResponse(BaseModel):
    """Response after initiating registration."""
    message: str
    pending_registration_id: int


class OTPVerifyRequest(BaseModel):
    """Request to verify OTP and complete registration."""
    pending_registration_id: int
    otp: str
