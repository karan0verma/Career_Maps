import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.db.base import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    google_id = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    profile_image = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    current_city = Column(String, nullable=True)
    current_state = Column(String, nullable=True)
    experience_level = Column(String, nullable=True)
    willing_to_relocate = Column(Boolean, default=False)
    hashed_password = Column(String, nullable=True)
    role = Column(String, default="USER")
    is_active = Column(Boolean, default=True)
    onboarding_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), primary_key=True)
    preferred_roles = Column(JSONB, default=list) # Array of strings
    preferred_industries = Column(JSONB, default=list)
    preferred_states = Column(JSONB, default=list)
    preferred_cities = Column(JSONB, default=list)
    preferred_work_modes = Column(JSONB, default=list)
    preferred_employment_types = Column(JSONB, default=list)
    skills = Column(JSONB, default=list)
    min_salary = Column(Integer, nullable=True)
    max_salary = Column(Integer, nullable=True)
    
    user = relationship("User", back_populates="preferences")

class SavedJob(Base):
    __tablename__ = "saved_jobs"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), primary_key=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.job_id"), primary_key=True)
    saved_at = Column(DateTime(timezone=True), server_default=func.now())
    job = relationship("Job")

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    query_text = Column(String)
    filters = Column(JSONB)
    result_count = Column(Integer)
    searched_at = Column(DateTime(timezone=True), server_default=func.now())

class AppliedJob(Base):
    __tablename__ = "applied_jobs"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), primary_key=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.job_id"), primary_key=True)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    job = relationship("Job")

class JobAlert(Base):
    __tablename__ = "job_alerts"
    
    alert_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    name = Column(String)
    filters = Column(JSONB)
    frequency = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), primary_key=True)
    notification_preferences = Column(JSONB)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ViewedJob(Base):
    __tablename__ = "viewed_jobs"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), primary_key=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.job_id"), primary_key=True)
    viewed_at = Column(DateTime(timezone=True), server_default=func.now())
    job = relationship("Job")

class NotificationQueue(Base):
    __tablename__ = "notification_queue"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    channel = Column(String)
    payload = Column(JSONB)
    status = Column(String, default="PENDING", index=True)
    retry_count = Column(Integer, default=0)
    scheduled_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    sent_at = Column(DateTime(timezone=True))
