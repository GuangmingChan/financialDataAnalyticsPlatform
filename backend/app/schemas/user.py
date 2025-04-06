from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    role: str = "student"

class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int

    class Config:
        orm_mode = True 