from pydantic import BaseModel, EmailStr
from typing import Optional
from app.db.models import RoleEnum

class UserBase(BaseModel):
    email: EmailStr
    role: Optional[RoleEnum] = RoleEnum.USER
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
