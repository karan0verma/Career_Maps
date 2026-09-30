from pydantic import BaseModel
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime
from src.schemas.job import Job

class SavedJobBase(BaseModel):
    job_id: UUID

class SavedJob(SavedJobBase):
    user_id: UUID
    saved_at: datetime
    job: Optional[Job] = None

    class Config:
        from_attributes = True

from src.schemas.job import JobWithCompany

class SavedJobWithCompanyDetails(SavedJobBase):
    user_id: UUID
    saved_at: datetime
    job: Optional[JobWithCompany] = None

    class Config:
        from_attributes = True

class ViewedJobBase(BaseModel):
    job_id: UUID

class ViewedJob(ViewedJobBase):
    user_id: UUID
    viewed_at: datetime
    job: Optional[Job] = None

    class Config:
        from_attributes = True

class ViewedJobWithCompanyDetails(ViewedJobBase):
    user_id: UUID
    viewed_at: datetime
    job: Optional[JobWithCompany] = None

    class Config:
        from_attributes = True

class SearchHistoryBase(BaseModel):
    query_text: Optional[str] = None
    filters: Optional[dict] = None

class SearchHistory(SearchHistoryBase):
    id: UUID
    user_id: Optional[UUID] = None
    result_count: int
    searched_at: datetime

    class Config:
        from_attributes = True
