from pydantic import BaseModel, EmailStr, field_validator 
from typing import Annotated 
from fastapi import Request, HTTPException, Depends 
import re


class UserValidationSchema(BaseModel):
    email: EmailStr                  
    password: str
    
    @field_validator('password')    
    @classmethod
    def validate_password(cls, v):
        if not re.match(r'^[a-zA-Z0-9]{8,30}$', v):
            raise ValueError(...)  
        return v
