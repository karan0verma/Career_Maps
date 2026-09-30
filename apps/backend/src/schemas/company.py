from pydantic import BaseModel, HttpUrl
from typing import Optional
from uuid import UUID
from datetime import datetime

class CompanyBase(BaseModel):
    official_name: str
    display_name: str
    website: str
    career_url: Optional[str] = None
    logo_url: Optional[str] = None
    hiring_status: Optional[str] = None
    company_size: Optional[str] = None
    headquarters: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    industry: Optional[str] = None
    company_type: Optional[str] = None
    is_active: Optional[bool] = True

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    official_name: Optional[str] = None
    display_name: Optional[str] = None
    website: Optional[str] = None
    career_url: Optional[str] = None
    logo_url: Optional[str] = None
    hiring_status: Optional[str] = None
    company_size: Optional[str] = None
    headquarters: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    industry: Optional[str] = None
    company_type: Optional[str] = None
    is_active: Optional[bool] = None

class Company(CompanyBase):
    company_id: UUID
    is_deleted: bool
    total_active_jobs: Optional[int] = None
    first_discovered_at: Optional[datetime] = None
    last_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
