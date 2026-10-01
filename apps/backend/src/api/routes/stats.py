from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any, Dict

from src.api import deps
from src.models.job import Job
from src.models.company import Company

router = APIRouter()

@router.get("/", response_model=Dict[str, int])
def get_platform_stats(db: Session = Depends(deps.get_db)) -> Any:
    companies_count = db.query(Company).filter(Company.is_active == True, Company.is_deleted == False).count()
    india_keywords = ['India', 'Bengaluru', 'Bangalore', 'Mumbai', 'Delhi', 'Gurugram', 'Gurgaon', 'Noida', 'Pune', 'Chennai', 'Hyderabad', 'Kolkata', 'Ahmedabad', 'Kochi', 'Jaipur', 'Chandigarh', 'Indore', 'Bhubaneswar', 'Dehradun', 'Ghaziabad', 'Faridabad']
    location_filters = [Job.location.ilike(f"%{kw}%") for kw in india_keywords]
    from sqlalchemy import or_
    
    jobs_count = db.query(Job).filter(
        Job.is_active == True, 
        Job.is_deleted == False,
        or_(
            Job.country.in_(['IN', 'in', 'India', 'india', 'IND', 'ind']),
            or_(*location_filters)
        )
    ).count()
    return {
        "companies": companies_count,
        "jobs": jobs_count
    }

from src.models.user import SiteStat

@router.post("/visit", response_model=Dict[str, int])
def record_visit(db: Session = Depends(deps.get_db)) -> Any:
    stat = db.query(SiteStat).filter(SiteStat.id == "global").first()
    if not stat:
        stat = SiteStat(id="global", visitor_count=1)
        db.add(stat)
    else:
        stat.visitor_count += 1
    db.commit()
    db.refresh(stat)
    return {"visitor_count": stat.visitor_count}

@router.get("/visit", response_model=Dict[str, int])
def get_visits(db: Session = Depends(deps.get_db)) -> Any:
    stat = db.query(SiteStat).filter(SiteStat.id == "global").first()
    return {"visitor_count": stat.visitor_count if stat else 0}
