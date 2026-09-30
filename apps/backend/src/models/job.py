import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.db.base import Base

class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.company_id"), index=True)
    external_job_id = Column(String, index=True)
    title = Column(String, nullable=False, index=True)
    department = Column(String, index=True)
    location = Column(String)
    country = Column(String, index=True)
    state = Column(String, index=True)
    city = Column(String, index=True)
    work_mode = Column(String, index=True)
    employment_type = Column(String, index=True)
    experience_level = Column(String, index=True)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    currency = Column(String)
    description = Column(Text)
    requirements = Column(Text)
    required_skills = Column(JSONB, default=list)
    apply_url = Column(String, unique=True, nullable=False)
    source_url = Column(String)
    raw_data = Column(JSONB)
    embedding_status = Column(String)
    embedding_updated_at = Column(DateTime(timezone=True))
    posted_at = Column(DateTime(timezone=True))
    first_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, index=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    company = relationship("Company", back_populates="jobs")
