import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from src.db.base import Base

class SchedulerMetadata(Base):
    __tablename__ = "scheduler_metadata"
    
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.company_id"), primary_key=True)
    crawl_frequency = Column(String)
    next_crawl_at = Column(DateTime(timezone=True), index=True)
    priority = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    last_success_at = Column(DateTime(timezone=True))
    last_failure_at = Column(DateTime(timezone=True))
    locked_until = Column(DateTime(timezone=True))

class CrawlHistory(Base):
    __tablename__ = "crawl_history"
    
    crawl_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.company_id"), nullable=True)
    trigger_type = Column(String)
    status = Column(String)
    extraction_strategy = Column(String, nullable=True)
    jobs_found = Column(Integer)
    jobs_added = Column(Integer)
    jobs_deactivated = Column(Integer)
    errors = Column(JSONB)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
