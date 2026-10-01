from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from uuid import UUID
from datetime import datetime

from src.api import deps
from src.models.job import Job
from src.models.company import Company
from src.models.user import User
from src.models.user import ViewedJob, SearchHistory
from src.schemas.job import JobWithCompany, JobRecommended
from src.models.user import UserPreferences

router = APIRouter()

@router.get("/recommended", response_model=List[JobRecommended])
def get_recommended_jobs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    # 1. Fetch user preferences
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.user_id).first()
    if not prefs:
        prefs = UserPreferences() # Empty default

    # 2. Fetch active jobs (limit to a reasonable number to score in memory, e.g., 1000)
    # Ideally, this should use SQL for scoring, but memory scoring is fine for prototype.
    query = db.query(Job).options(joinedload(Job.company)).filter(
        Job.is_active == True, 
        Job.is_deleted == False
    )
    
    # Pre-filter by country
    query = query.filter(
        or_(
            Job.country.in_(['IN', 'in', 'India', 'india', 'IND', 'ind']),
            Job.location.ilike("%India%"),
            Job.location.ilike("%Bengaluru%"),
            Job.location.ilike("%Bangalore%"),
            Job.location.ilike("%Mumbai%"),
            Job.location.ilike("%Delhi%"),
            Job.location.ilike("%Pune%"),
            Job.location.ilike("%Hyderabad%"),
            Job.location.ilike("%Chennai%")
        )
    )
    
    jobs = query.order_by(Job.first_seen_at.desc()).limit(500).all()

    recommended_jobs = []
    
    for job in jobs:
        score = 0
        reasons = []
        
        # 1. Role match (+50 max)
        if prefs.preferred_roles and job.title:
            role_matched_exact = False
            role_matched_partial = False
            for role in prefs.preferred_roles:
                role_lower = role.lower()
                title_lower = job.title.lower()
                
                # Direct match
                if role_lower in title_lower or title_lower in role_lower:
                    role_matched_exact = True
                    break
                
                # Partial match
                role_words = set(role_lower.split())
                title_words = set(title_lower.split())
                stop_words = {'and', 'or', 'senior', 'junior', 'lead', 'manager', 'associate', 'staff', 'developer', 'engineer'}
                role_words = role_words - stop_words
                title_words = title_words - stop_words
                if len(role_words.intersection(title_words)) >= 1:
                    role_matched_partial = True
                    
            if role_matched_exact:
                score += 50
                reasons.append("Role matches exactly")
            elif role_matched_partial:
                score += 25
                reasons.append("Partial role match")
                
        # 2. Location match (+20)
        if prefs.preferred_states and (job.state or job.location):
            loc_matched = False
            for state in prefs.preferred_states:
                if state.lower() in (job.state or "").lower() or state.lower() in (job.location or "").lower():
                    loc_matched = True
                    break
            if loc_matched:
                score += 20
                reasons.append("✓ Location matches")
                
        # 3. Authentic Skill Match (up to +40)
        if prefs.skills and getattr(job, 'required_skills', None):
            user_skills = set(s.lower().strip() for s in prefs.skills)
            job_skills = set(s.lower().strip() for s in job.required_skills)
            
            if job_skills:
                overlap = user_skills.intersection(job_skills)
                match_ratio = len(overlap) / len(job_skills)
                
                if overlap:
                    skill_points = int(match_ratio * 40)
                    score += skill_points
                    
                    # Capitalize for display
                    display_skills = [s.title() for s in list(overlap)[:3]]
                    matched_names = ", ".join(display_skills)
                    if len(overlap) > 3:
                        matched_names += f" and {len(overlap)-3} more"
                    reasons.append(f"✓ Skills match: {matched_names}")
                
        # 4. Work mode match (+10)
        if prefs.preferred_work_modes and job.work_mode:
            mode_matched = False
            for mode in prefs.preferred_work_modes:
                if mode.lower() in job.work_mode.lower():
                    mode_matched = True
                    break
            if mode_matched:
                score += 10
                reasons.append(f"✓ Work mode matches")
                
        # 5. Employment type match (+10)
        if prefs.preferred_employment_types and job.employment_type:
            type_matched = False
            for emp_type in prefs.preferred_employment_types:
                if emp_type.lower() in job.employment_type.lower():
                    type_matched = True
                    break
            if type_matched:
                score += 10
                reasons.append(f"✓ Employment type matches")

        # Normalize score to percentage (max is 100)
        match_percentage = min(100, score)
        
        if match_percentage > 0:
            job_dict = {column.name: getattr(job, column.name) for column in job.__table__.columns}
            job_dict["company"] = job.company
            job_dict["match_percentage"] = match_percentage
            job_dict["match_reasons"] = reasons
            recommended_jobs.append(job_dict)

    # Sort by score descending
    recommended_jobs.sort(key=lambda x: x["match_percentage"], reverse=True)
    
    return recommended_jobs[skip:skip+limit]

import meilisearch

# Initialize Meilisearch client once (in production this should be in a dependency or global config)
try:
    meili_client = meilisearch.Client('http://127.0.0.1:7700')
except Exception:
    meili_client = None

@router.get("/", response_model=List[JobWithCompany])
def search_jobs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    q: Optional[str] = None,
    location: Optional[str] = None,
    work_mode: Optional[str] = None,
    domain: Optional[str] = None,
    experience: Optional[str] = None,
    role: Optional[str] = None,
    company_id: Optional[UUID] = None,
    company_type: Optional[str] = None,
    current_user: Optional[User] = Depends(deps.get_optional_current_user)
) -> Any:
    # Query DB directly for comprehensive multi-attribute filtering
    query = db.query(Job).options(joinedload(Job.company)).filter(Job.is_active == True, Job.is_deleted == False)
    
    if company_type:
        query = query.join(Job.company).filter(Company.company_type.ilike(f"%{company_type}%"))
        
    if q:
        # Avoid duplicate join if already joined
        if not company_type:
            query = query.join(Job.company)
        query = query.filter(
            or_(
                Job.title.ilike(f"%{q}%"),
                Job.description.ilike(f"%{q}%"),
                Job.requirements.ilike(f"%{q}%"),
                Company.display_name.ilike(f"%{q}%")
            )
        )
    if location:
        query = query.filter(
            or_(
                Job.location.ilike(f"%{location}%"),
                Job.country.ilike(f"%{location}%"),
                Job.city.ilike(f"%{location}%")
            )
        )
    if work_mode:
        query = query.filter(Job.work_mode.ilike(f"%{work_mode}%"))
    if company_id:
        query = query.filter(Job.company_id == company_id)

    # Domain filtering
    if domain and domain.lower() != "all":
        d_lower = domain.lower()
        if "tech" in d_lower or "software" in d_lower:
            query = query.filter(or_(
                Job.requirements.ilike("%technology%"),
                Job.title.ilike("%engineer%"),
                Job.title.ilike("%developer%"),
                Job.title.ilike("%architect%"),
                Job.title.ilike("%lead%")
            ))
        elif "infra" in d_lower or "cloud" in d_lower:
            query = query.filter(or_(
                Job.requirements.ilike("%infrastructure%"),
                Job.requirements.ilike("%itis%"),
                Job.requirements.ilike("%cloud%"),
                Job.requirements.ilike("%devops%"),
                Job.title.ilike("%infra%"),
                Job.title.ilike("%administrator%"),
                Job.title.ilike("%network%")
            ))
        elif "bps" in d_lower or "process" in d_lower or "operations" in d_lower:
            query = query.filter(or_(
                Job.requirements.ilike("%business process%"),
                Job.requirements.ilike("%bps%"),
                Job.requirements.ilike("%operations%"),
                Job.title.ilike("%process%"),
                Job.title.ilike("%associate%"),
                Job.title.ilike("%operations%")
            ))
        elif "consult" in d_lower:
            query = query.filter(or_(
                Job.requirements.ilike("%consult%"),
                Job.title.ilike("%consultant%"),
                Job.requirements.ilike("%sap%"),
                Job.requirements.ilike("%oracle%"),
                Job.requirements.ilike("%infor%")
            ))
        elif "qa" in d_lower or "test" in d_lower:
            query = query.filter(or_(
                Job.requirements.ilike("%quality%"),
                Job.requirements.ilike("%qa%"),
                Job.requirements.ilike("%testing%"),
                Job.title.ilike("%test%"),
                Job.title.ilike("%qa%"),
                Job.title.ilike("%automation%")
            ))
        elif "finance" in d_lower or "account" in d_lower:
            query = query.filter(or_(
                Job.requirements.ilike("%finance%"),
                Job.requirements.ilike("%accounting%"),
                Job.title.ilike("%account%"),
                Job.title.ilike("%finance%"),
                Job.title.ilike("%receivables%"),
                Job.title.ilike("%payables%")
            ))
        elif "hr" in d_lower or "human" in d_lower:
            query = query.filter(or_(
                Job.requirements.ilike("%human resources%"),
                Job.requirements.ilike("%hr%"),
                Job.title.ilike("%hr%"),
                Job.title.ilike("%recruiter%"),
                Job.title.ilike("%talent%")
            ))
        else:
            query = query.filter(or_(
                Job.requirements.ilike(f"%{domain}%"),
                Job.title.ilike(f"%{domain}%"),
                Job.description.ilike(f"%{domain}%")
            ))

    # Experience level filtering
    if experience and experience.lower() != "all":
        exp_lower = experience.lower()
        if "0-2" in exp_lower or "entry" in exp_lower:
            query = query.filter(or_(
                Job.experience_level.ilike("%0-1%"),
                Job.experience_level.ilike("%0-2%"),
                Job.experience_level.ilike("%1-2%"),
                Job.experience_level.ilike("%1-3%"),
                Job.experience_level.ilike("%0 to 2%"),
                Job.experience_level.ilike("%fresh%"),
                Job.experience_level.ilike("%entry%")
            ))
        elif "2-5" in exp_lower or "mid" in exp_lower:
            query = query.filter(or_(
                Job.experience_level.ilike("%2-%"),
                Job.experience_level.ilike("%3-%"),
                Job.experience_level.ilike("%4-%"),
                Job.experience_level.ilike("%2 to 5%"),
                Job.experience_level.ilike("%3 to 5%"),
                Job.experience_level.ilike("%2-4%"),
                Job.experience_level.ilike("%2-5%"),
                Job.experience_level.ilike("%2-8%")
            ))
        elif "5-8" in exp_lower or "senior" in exp_lower:
            query = query.filter(or_(
                Job.experience_level.ilike("%5-%"),
                Job.experience_level.ilike("%6-%"),
                Job.experience_level.ilike("%7-%"),
                Job.experience_level.ilike("%5 to 8%"),
                Job.experience_level.ilike("%6 to 8%"),
                Job.experience_level.ilike("%6-12%"),
                Job.experience_level.ilike("%5-10%")
            ))
        elif "8+" in exp_lower or "lead" in exp_lower:
            query = query.filter(or_(
                Job.experience_level.ilike("%8-%"),
                Job.experience_level.ilike("%9-%"),
                Job.experience_level.ilike("%10-%"),
                Job.experience_level.ilike("%12-%"),
                Job.experience_level.ilike("%14-%"),
                Job.experience_level.ilike("%15-%"),
                Job.experience_level.ilike("%8+ %"),
                Job.experience_level.ilike("%10+ %")
            ))
        else:
            query = query.filter(Job.experience_level.ilike(f"%{experience}%"))

    # Role archetype filtering
    if role and role.lower() != "all":
        query = query.filter(or_(
            Job.title.ilike(f"%{role}%"),
            Job.requirements.ilike(f"%{role}%")
        ))
        
    jobs = query.order_by(Job.first_seen_at.desc()).offset(skip).limit(limit).all()
    
    # Log search history if user is authenticated and searched for something
    if current_user and (q or location or work_mode or company_id):
        filters = {}
        if location: filters["location"] = location
        if work_mode: filters["work_mode"] = work_mode
        if company_id: filters["company_id"] = str(company_id)
        
        history = SearchHistory(
            user_id=current_user.user_id,
            query_text=q,
            filters=filters,
            result_count=len(jobs),
            searched_at=datetime.utcnow()
        )
        db.add(history)
        db.commit()
        
    return jobs

@router.get("/{job_id}", response_model=JobWithCompany)
def get_job(
    job_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_optional_current_user)
) -> Any:
    job = db.query(Job).options(joinedload(Job.company)).filter(Job.job_id == job_id, Job.is_deleted == False).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if current_user:
        # Log to viewed_jobs
        view = ViewedJob(
            user_id=current_user.user_id,
            job_id=job.job_id,
            viewed_at=datetime.utcnow()
        )
        db.add(view)
        db.commit()
        
    return job
