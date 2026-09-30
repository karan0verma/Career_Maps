from typing import Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID

class Token(BaseModel):
    access_token: str
    token_type: str

class GoogleToken(BaseModel):
    token: str

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    name: str
    phone: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    name: Optional[str] = None
    profile_image: Optional[str] = None
    phone: Optional[str] = None
    current_city: Optional[str] = None
    current_state: Optional[str] = None
    experience_level: Optional[str] = None
    willing_to_relocate: Optional[bool] = None

class UserInDBBase(UserBase):
    user_id: UUID
    role: str
    is_active: bool
    name: Optional[str] = None
    profile_image: Optional[str] = None
    phone: Optional[str] = None
    current_city: Optional[str] = None
    current_state: Optional[str] = None
    experience_level: Optional[str] = None
    willing_to_relocate: Optional[bool] = None
    onboarding_completed: bool = False

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass
class UserPreferencesBase(BaseModel):
    preferred_roles: list[str] = []
    preferred_industries: list[str] = []
    preferred_states: list[str] = []
    preferred_cities: list[str] = []
    preferred_work_modes: list[str] = []
    preferred_employment_types: list[str] = []
    skills: list[str] = []
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None

class UserPreferencesUpdate(UserPreferencesBase):
    pass

class UserPreferences(UserPreferencesBase):
    user_id: UUID

    class Config:
        from_attributes = True
