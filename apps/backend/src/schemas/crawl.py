from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class CrawlHistoryBase(BaseModel):
    trigger_type: str
    status: str
    jobs_found: Optional[int] = 0
    jobs_added: Optional[int] = 0
    jobs_deactivated: Optional[int] = 0
    errors: Optional[Dict[str, Any]] = None

class CrawlHistory(CrawlHistoryBase):
    crawl_id: UUID
    company_id: Optional[UUID] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CrawlTriggerRequest(BaseModel):
    trigger_type: Optional[str] = "MANUAL"

class CrawlBatchRequest(BaseModel):
    company_ids: List[UUID]
