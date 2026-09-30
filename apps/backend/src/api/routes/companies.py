from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from uuid import UUID

from src.api import deps
from src.models.company import Company
from src.models.job import Job
from src.schemas.company import Company as CompanySchema

router = APIRouter()

import meilisearch

try:
    meili_client = meilisearch.Client('http://127.0.0.1:7700')
except Exception:
    meili_client = None

@router.get("/", response_model=List[CompanySchema])
def get_companies(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> Any:
    # Try Meilisearch first if we have a text query
    use_meili = False
    meili_comp_ids = []
    
    if meili_client and search:
        try:
            index = meili_client.index('companies')
            
            search_params = {
                'offset': skip,
                'limit': limit,
            }
            
            search_res = index.search(search, search_params)
            
            meili_comp_ids = [hit['id'] for hit in search_res['hits']]
            use_meili = True
        except Exception as e:
            print(f"Meilisearch error: {e}")
            use_meili = False
            
    if use_meili:
        if not meili_comp_ids:
            return []
        else:
            query = db.query(Company).filter(
                Company.company_id.in_(meili_comp_ids),
                Company.is_active == True,
                Company.is_deleted == False
            )
            db_companies = {str(c.company_id): c for c in query.all()}
            return [db_companies[cid] for cid in meili_comp_ids if cid in db_companies]
    query = db.query(Company).filter(
        Company.is_active == True, 
        Company.is_deleted == False
    )
    
    if search:
        query = query.filter(Company.display_name.ilike(f"%{search}%"))
        
    comps = query.offset(skip).limit(limit).all()
    for c in comps:
        cnt = db.query(Job).filter(
            Job.company_id == c.company_id,
            Job.is_active == True,
            Job.is_deleted == False
        ).count()
        setattr(c, "total_active_jobs", cnt)
    return comps

@router.get("/{company_id}", response_model=CompanySchema)
def get_company(
    company_id: UUID,
    db: Session = Depends(deps.get_db)
) -> Any:
    company = db.query(Company).filter(
        Company.company_id == company_id,
        Company.is_deleted == False
    ).first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    job_count = db.query(Job).filter(
        Job.company_id == company_id,
        Job.is_active == True,
        Job.is_deleted == False
    ).count()
    setattr(company, "total_active_jobs", job_count)
    return company
