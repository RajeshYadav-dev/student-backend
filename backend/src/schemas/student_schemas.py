from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserShow(BaseModel):
    std_id: str
    name: str
    email: EmailStr
    phone_number: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    standard: Optional[str] = None
    profile_pic_url: Optional[str] = None
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enables ORM conversion

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    phone_number: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    standard: Optional[str] = None
    profile_pic_url: Optional[str] = None
    is_active: bool = False  # Default to inactive on creation

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    standard: Optional[str] = None
    profile_pic_url: Optional[str] = None
    is_active: Optional[bool] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    
class CreateAdmin(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    phone_number: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    standard: Optional[str] = None
    profile_pic_url: Optional[str] = None
    is_active: bool = False 
    role: str = "admin"    
