from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from src.schemas.company import Company

class JobBase(BaseModel):
    external_job_id: Optional[str] = None
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    work_mode: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    required_skills: Optional[List[str]] = None
    apply_url: Optional[str] = None
    source_url: Optional[str] = None
    posted_at: Optional[datetime] = None

class Job(JobBase):
    job_id: UUID
    company_id: UUID
    is_active: bool
    is_deleted: bool
    first_seen_at: datetime
    last_seen_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class JobWithCompany(Job):
    company: Optional[Company] = None

class JobRecommended(JobWithCompany):
    match_percentage: int
    match_reasons: List[str]
