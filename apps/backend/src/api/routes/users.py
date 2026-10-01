from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from src.core import security
from src.api import deps
from src.models.user import User
from src.schemas.user import UserUpdate, User as UserSchema
from src.schemas.user_actions import SavedJob as SavedJobSchema, ViewedJob as ViewedJobSchema, SearchHistory as SearchHistorySchema, SavedJobWithCompanyDetails, ViewedJobWithCompanyDetails, AppliedJobSchema, AppliedJobWithCompanyDetails
from src.models.user import SavedJob, ViewedJob, SearchHistory, AppliedJob
from src.models.job import Job
from uuid import UUID
from datetime import datetime

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=UserSchema)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    if user_in.email:
        user_with_email = db.query(User).filter(User.email == user_in.email).first()
        if user_with_email and user_with_email.user_id != current_user.user_id:
            raise HTTPException(
                status_code=400, detail="User with this email already exists"
            )
        current_user.email = user_in.email
    if user_in.password:
        current_user.hashed_password = security.get_password_hash(user_in.password)
    
    # Update other profile fields
    update_data = user_in.dict(exclude_unset=True)
    for field in ["name", "profile_image", "phone", "current_city", "current_state", "experience_level", "willing_to_relocate"]:
        if field in update_data:
            setattr(current_user, field, update_data[field])
            
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

from src.models.user import UserPreferences
from src.schemas.user import UserPreferences as UserPreferencesSchema, UserPreferencesUpdate

@router.get("/me/preferences", response_model=UserPreferencesSchema)
def get_user_preferences(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.user_id).first()
    if not prefs:
        prefs = UserPreferences(user_id=current_user.user_id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return prefs

@router.put("/me/preferences", response_model=UserPreferencesSchema)
def update_user_preferences(
    *,
    db: Session = Depends(deps.get_db),
    prefs_in: UserPreferencesUpdate,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.user_id).first()
    if not prefs:
        prefs = UserPreferences(user_id=current_user.user_id)
        db.add(prefs)
        
    update_data = prefs_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prefs, field, value)
        
    # Mark onboarding as completed
    current_user.onboarding_completed = True
        
    db.commit()
    db.refresh(prefs)
    return prefs

@router.post("/me/saved_jobs", response_model=SavedJobWithCompanyDetails)
def save_job(
    *,
    db: Session = Depends(deps.get_db),
    job_id: UUID,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    job = db.query(Job).filter(Job.job_id == job_id, Job.is_deleted == False).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    saved = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.user_id,
        SavedJob.job_id == job_id
    ).first()
    
    if not saved:
        saved = SavedJob(
            user_id=current_user.user_id,
            job_id=job_id,
            saved_at=datetime.utcnow()
        )
        db.add(saved)
        db.commit()
        db.refresh(saved)
        
    return saved

@router.get("/me/saved_jobs", response_model=List[SavedJobWithCompanyDetails])
def list_saved_jobs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    return db.query(SavedJob).options(joinedload(SavedJob.job).joinedload(Job.company)).filter(SavedJob.user_id == current_user.user_id).order_by(SavedJob.saved_at.desc()).offset(skip).limit(limit).all()

@router.delete("/me/saved_jobs/{job_id}")
def remove_saved_job(
    *,
    db: Session = Depends(deps.get_db),
    job_id: UUID,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    saved = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.user_id,
        SavedJob.job_id == job_id
    ).first()
    
    if saved:
        db.delete(saved)
        db.commit()
        
    return {"message": "Job unsaved"}

@router.post("/me/applied_jobs", response_model=AppliedJobWithCompanyDetails)
def apply_job(
    *,
    db: Session = Depends(deps.get_db),
    job_id: UUID,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    job = db.query(Job).filter(Job.job_id == job_id, Job.is_deleted == False).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    applied = db.query(AppliedJob).filter(
        AppliedJob.user_id == current_user.user_id,
        AppliedJob.job_id == job_id
    ).first()
    
    if not applied:
        applied = AppliedJob(user_id=current_user.user_id, job_id=job_id)
        db.add(applied)
        db.commit()
        db.refresh(applied)
        
    return applied

@router.get("/me/applied_jobs", response_model=List[AppliedJobWithCompanyDetails])
def list_applied_jobs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    return db.query(AppliedJob).options(joinedload(AppliedJob.job).joinedload(Job.company)).filter(AppliedJob.user_id == current_user.user_id).order_by(AppliedJob.applied_at.desc()).offset(skip).limit(limit).all()

@router.get("/me/viewed_jobs", response_model=List[ViewedJobWithCompanyDetails])
def list_viewed_jobs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    return db.query(ViewedJob).options(joinedload(ViewedJob.job).joinedload(Job.company)).filter(ViewedJob.user_id == current_user.user_id).order_by(ViewedJob.viewed_at.desc()).offset(skip).limit(limit).all()

@router.get("/me/search_history", response_model=List[SearchHistorySchema])
def list_search_history(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    return db.query(SearchHistory).filter(SearchHistory.user_id == current_user.user_id).order_by(SearchHistory.searched_at.desc()).offset(skip).limit(limit).all()
