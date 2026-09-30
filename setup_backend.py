import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

base_dir = "apps/backend"

requirements = """fastapi==0.111.0
uvicorn==0.29.0
sqlalchemy==2.0.30
alembic==1.13.1
psycopg2-binary==2.9.9
pydantic==2.7.1
pydantic-settings==2.2.1
python-dotenv==1.0.1
structlog==24.1.0
"""

config_py = """import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Career Maps API"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/careermaps")
    
    class Config:
        env_file = ".env"

settings = Settings()
"""

db_base_py = """from sqlalchemy.orm import declarative_base

Base = declarative_base()
"""

db_session_py = """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""

models_init_py = """from src.db.base import Base
from .user import User, SavedJob, SearchHistory, JobAlert
from .company import Company, CompanyAlias, CompanyATSHistory
from .job import Job
from .scheduler import SchedulerMetadata, CrawlHistory
"""

models_user_py = """import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from src.db.base import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="USER")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SavedJob(Base):
    __tablename__ = "saved_jobs"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), primary_key=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.job_id"), primary_key=True)
    saved_at = Column(DateTime(timezone=True), server_default=func.now())

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    query_text = Column(String)
    filters = Column(JSONB)
    result_count = Column(String) # Could be int
    searched_at = Column(DateTime(timezone=True), server_default=func.now())

class JobAlert(Base):
    __tablename__ = "job_alerts"
    
    alert_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    name = Column(String)
    filters = Column(JSONB)
    frequency = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
"""

models_company_py = """import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
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
"""

models_job_py = """import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
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
    apply_url = Column(String, unique=True, nullable=False)
    source_url = Column(String)
    raw_data = Column(JSONB)
    posted_at = Column(DateTime(timezone=True))
    first_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, index=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
"""

models_scheduler_py = """import uuid
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
    jobs_found = Column(Integer)
    jobs_added = Column(Integer)
    jobs_deactivated = Column(Integer)
    errors = Column(JSONB)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
"""

main_py = """from fastapi import FastAPI
from src.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
"""

create_file(f"{base_dir}/requirements.txt", requirements)
create_file(f"{base_dir}/src/core/config.py", config_py)
create_file(f"{base_dir}/src/db/base.py", db_base_py)
create_file(f"{base_dir}/src/db/session.py", db_session_py)
create_file(f"{base_dir}/src/models/__init__.py", models_init_py)
create_file(f"{base_dir}/src/models/user.py", models_user_py)
create_file(f"{base_dir}/src/models/company.py", models_company_py)
create_file(f"{base_dir}/src/models/job.py", models_job_py)
create_file(f"{base_dir}/src/models/scheduler.py", models_scheduler_py)
create_file(f"{base_dir}/src/main.py", main_py)

print("Scaffold complete.")
