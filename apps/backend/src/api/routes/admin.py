import csv
import io
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID

from src.api import deps
from src.models.user import User
from src.models.company import Company
from src.schemas.company import Company as CompanySchema, CompanyCreate, CompanyUpdate
from src.schemas.crawl import CrawlHistory as CrawlHistorySchema, CrawlTriggerRequest, CrawlBatchRequest
from src.models.scheduler import CrawlHistory
from src.services.crawler import CrawlerService

router = APIRouter()

# --- Company CRUD ---

@router.get("/companies", response_model=List[CompanySchema])
def list_companies(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(deps.get_current_active_admin)
) -> Any:
    return db.query(Company).filter(Company.is_deleted == False).offset(skip).limit(limit).all()

@router.post("/companies", response_model=CompanySchema)
def create_company(
    *,
    db: Session = Depends(deps.get_db),
    company_in: CompanyCreate,
    current_admin: User = Depends(deps.get_current_active_admin)
) -> Any:
    company = db.query(Company).filter(Company.website == company_in.website).first()
    if company:
        raise HTTPException(status_code=400, detail="Company with this website already exists")
    
    company = Company(
        official_name=company_in.official_name,
        display_name=company_in.display_name,
        website=company_in.website,
        career_url=company_in.career_url,
        industry=company_in.industry,
        country=company_in.country,
        city=company_in.city,
        is_active=company_in.is_active
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@router.put("/companies/{company_id}", response_model=CompanySchema)
def update_company(
    *,
    db: Session = Depends(deps.get_db),
    company_id: UUID,
    company_in: CompanyUpdate,
    current_admin: User = Depends(deps.get_current_active_admin)
) -> Any:
    company = db.query(Company).filter(Company.company_id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    update_data = company_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)
        
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@router.delete("/companies/{company_id}", response_model=CompanySchema)
def delete_company(
    *,
    db: Session = Depends(deps.get_db),
    company_id: UUID,
    current_admin: User = Depends(deps.get_current_active_admin)
) -> Any:
    company = db.query(Company).filter(Company.company_id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    company.is_deleted = True
    company.is_active = False
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

# --- CSV Bulk Import ---

@router.post("/companies/import")
def import_companies_csv(
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    current_admin: User = Depends(deps.get_current_active_admin)
) -> Any:
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    
    imported = 0
    updated = 0
    
    for row in reader:
        domain = row.get("Domain", row.get("domain", "")).strip()
        if not domain:
            continue
            
        company_name = row.get("Company Name", row.get("company_name", domain)).strip()
        career_url = row.get("Career URL", row.get("career_url", "")).strip() or None
        
        company = db.query(Company).filter(Company.website.ilike(f"%{domain}%")).first()
        if company:
            if not company.career_url and career_url:
                company.career_url = career_url
                updated += 1
        else:
            new_company = Company(
                official_name=company_name,
                display_name=company_name,
                website=domain,
                career_url=career_url,
                is_active=True
            )
            db.add(new_company)
            imported += 1
            
    db.commit()
    return {"message": "CSV import complete", "imported": imported, "updated": updated}

# --- Crawl Orchestration ---

@router.post("/companies/{company_id}/crawl", response_model=CrawlHistorySchema)
def trigger_crawl(
    *,
    db: Session = Depends(deps.get_db),
    company_id: UUID,
    request: CrawlTriggerRequest,
    current_admin: User = Depends(deps.get_current_active_admin)
) -> Any:
    history = CrawlerService.run_crawl(db, company_id, trigger_type=request.trigger_type)
    return history

@router.post("/crawls/batch")
def trigger_batch_crawl(
    *,
    db: Session = Depends(deps.get_db),
    request: CrawlBatchRequest,
    current_admin: User = Depends(deps.get_current_active_admin)
) -> Any:
    # In a real MVP, this might push to a task queue (like Celery/APScheduler)
    # For now we'll do them sequentially or return a status saying they'll be processed
    results = []
    for cid in request.company_ids:
        res = CrawlerService.run_crawl(db, cid, trigger_type="BATCH")
        results.append({"company_id": cid, "status": res.status})
    return {"message": "Batch crawl completed", "results": results}

@router.get("/crawls", response_model=List[CrawlHistorySchema])
def list_crawls(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(deps.get_current_active_admin)
) -> Any:
    return db.query(CrawlHistory).order_by(CrawlHistory.started_at.desc()).offset(skip).limit(limit).all()

@router.post("/crawls/{crawl_id}/retry", response_model=CrawlHistorySchema)
def retry_crawl(
    *,
    db: Session = Depends(deps.get_db),
    crawl_id: UUID,
    current_admin: User = Depends(deps.get_current_active_admin)
) -> Any:
    crawl = db.query(CrawlHistory).filter(CrawlHistory.crawl_id == crawl_id).first()
    if not crawl:
        raise HTTPException(status_code=404, detail="Crawl not found")
        
    return CrawlerService.run_crawl(db, crawl.company_id, trigger_type="RETRY")
