import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Float, UniqueConstraint, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.db.base import Base

class Company(Base):
    __tablename__ = "companies"

    company_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    official_name = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    logo_url = Column(String)
    website = Column(String, unique=True, nullable=False)
    career_url = Column(String)
    hiring_status = Column(String)
    company_size = Column(String)
    headquarters = Column(String)
    country = Column(String, index=True)
    state = Column(String, index=True)
    city = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    industry = Column(String, index=True)
    company_type = Column(String)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    first_discovered_at = Column(DateTime(timezone=True), server_default=func.now())
    last_verified_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    jobs = relationship("Job", back_populates="company")

class CompanyAlias(Base):
    __tablename__ = "company_aliases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.company_id"), index=True)
    alias = Column(String, index=True)

class CompanyATSHistory(Base):
    __tablename__ = "company_ats_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.company_id"), index=True)
    ats_provider = Column(String, nullable=False)
    confidence_score = Column(Float)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    last_verified_at = Column(DateTime(timezone=True))
    is_current = Column(Boolean, index=True, default=True)

class CompanySource(Base):
    __tablename__ = "company_sources"
    __table_args__ = (
        UniqueConstraint('company_id', 'source_url', 'extraction_strategy', name='uq_company_source'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.company_id"), index=True)
    source_url = Column(String, nullable=False)
    extraction_strategy = Column(String, nullable=False)
    extraction_config = Column(JSON, nullable=True)
    health_status = Column(String, default='ACTIVE')
    last_verified_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class GlobalCompanyExpansion(Base):
    __tablename__ = "global_company_expansions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String, nullable=False, unique=True)
    career_portal_url = Column(String, nullable=False)
    global_openings_count = Column(Float, default=0)
    india_openings_count = Column(Float, default=0)
    primary_global_regions = Column(JSON, nullable=True)
    ats_platform = Column(String, nullable=True)
    expansion_status = Column(String, default="TRACKED_FOR_FUTURE_GLOBAL_PHASE")
    notes = Column(String, nullable=True)
    last_verified_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

