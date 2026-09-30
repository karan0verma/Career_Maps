import os
import sys
import json
import uuid
import re
import datetime
import urllib.request
from typing import List, Dict, Any
from uuid import UUID

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job
from src.portal_engine.normalizer import JobNormalizer

INFOSYS_COMPANY_ID = UUID('8b6e2d14-0e31-419b-9c71-29e557b71900')

def clean_skills(raw_skills: str) -> List[str]:
    if not raw_skills:
        return ["Technology", "Software Engineering"]
    cleaned = []
    # format: Domain->Healthcare->Regulatory Compliance & Standards,Technology->Life Sciences->Regulatory Systems
    parts = raw_skills.split(',')
    for p in parts:
        subparts = [s.strip() for s in p.split('->') if s.strip()]
        if subparts:
            leaf = subparts[-1]
            if leaf.lower() != "all" and len(leaf) > 2 and leaf not in cleaned:
                cleaned.append(leaf)
    return cleaned if cleaned else ["Technology", "Software Engineering"]

def import_infosys_jobs() -> int:
    print("=" * 75)
    print("STARTING LIVE EXTRACTION & INGESTION FOR INFOSYS LIMITED")
    print("=" * 75, flush=True)

    db = SessionLocal()
    
    # 1. Create or get Infosys Company Record
    company = db.query(Company).filter(Company.company_id == INFOSYS_COMPANY_ID).first()
    if not company:
        company = db.query(Company).filter(Company.display_name.ilike('%infosys%')).first()
        
    if not company:
        company = Company(
            company_id=INFOSYS_COMPANY_ID,
            official_name="Infosys Limited",
            display_name="Infosys Limited",
            website="https://www.infosys.com",
            career_url="https://career.infosys.com/joblist",
            logo_url="https://upload.wikimedia.org/wikipedia/commons/9/95/Infosys_logo.svg",
            industry="IT Services & Consulting",
            headquarters="Bengaluru, Karnataka, India",
            is_active=True,
            is_deleted=False
        )
        db.add(company)
    else:
        company.is_active = True
        company.is_deleted = False
        company.career_url = "https://career.infosys.com/joblist"
        company.logo_url = "https://upload.wikimedia.org/wikipedia/commons/9/95/Infosys_logo.svg"
    
    db.commit()
    print(f"1. Company Record: {company.display_name} (ID: {company.company_id})", flush=True)

    # 2. Extract from Infosys INTAP Gateway
    url = "https://intapgateway.infosysapps.com/careersci/search/intapjbsrch/getCareerSearchJobs?sourceId=1&searchText=ALL"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://career.infosys.com/joblist',
        'Origin': 'https://career.infosys.com'
    }

    print("2. Fetching live job vacancies from Infosys INTAP Gateway...", flush=True)
    req = urllib.request.Request(url, headers=headers)
    res = urllib.request.urlopen(req, timeout=25)
    raw_jobs = json.loads(res.read().decode('utf-8'))
    print(f"   -> Retrieved {len(raw_jobs)} live job vacancies from official portal!", flush=True)

    # 3. Clean previous jobs for Infosys
    deleted_cnt = db.query(Job).filter(Job.company_id == company.company_id).delete()
    db.commit()
    print(f"3. Refreshed table state (cleared {deleted_cnt} previous jobs)", flush=True)

    # 4. Normalize and Ingest
    now = datetime.datetime.now(datetime.timezone.utc)
    inserted = 0
    seen_codes = set()

    for item in raw_jobs:
        ref_code = item.get('referenceCode') or f"INFSYS-{item.get('postingId')}"
        if ref_code in seen_codes:
            continue
        seen_codes.add(ref_code)

        title = (item.get('postingTitle') or "Software Engineer").strip()
        loc_raw = (item.get('location') or "Bengaluru").strip().title()
        location = f"{loc_raw}, India"
        
        min_e = item.get('minExperienceLevel', 2)
        max_e = item.get('maxExperienceLevel', 8)
        exp_level = f"{min_e}-{max_e} Years"
        
        func_area = item.get('functionalArea') or "Technology"
        skills = clean_skills(item.get('preferredSkills', ''))
        if func_area and func_area not in skills:
            skills.append(func_area)

        # Build rich structured description
        desc_parts = []
        if item.get('postingDescription'):
            desc_parts.append(item.get('postingDescription').strip())
        if item.get('rolesResponsibilities'):
            desc_parts.append(f"Roles & Responsibilities:\n{item.get('rolesResponsibilities').strip()}")
        if item.get('technicalRequirement'):
            desc_parts.append(f"Technical Requirements:\n{item.get('technicalRequirement').strip()}")
        if item.get('additionalResponsibility'):
            desc_parts.append(f"Additional Responsibilities:\n{item.get('additionalResponsibility').strip()}")

        full_description = "\n\n".join(desc_parts) if desc_parts else f"Infosys Limited is hiring for {title}.\nLocation: {location}\nExperience: {exp_level}"
        apply_url = f"https://career.infosys.com/jobdesc?jobReferenceCode={ref_code}&companyhiringtype=IL&countrycode=IN"

        job = Job(
            job_id=uuid.uuid4(),
            company_id=company.company_id,
            title=title,
            location=location,
            city=loc_raw,
            country="India",
            work_mode="On-site / Hybrid",
            employment_type="Full-time",
            experience_level=exp_level,
            required_skills=skills,
            description=full_description,
            requirements=f"Experience: {exp_level} | Function: {func_area} | Reference: {ref_code} | Skills: {', '.join(skills)}",
            apply_url=apply_url,
            is_active=True,
            is_deleted=False,
            first_seen_at=now,
            last_seen_at=now
        )
        db.add(job)
        inserted += 1

    db.commit()
    db.close()

    print(f"4. Successfully Ingested {inserted} Verified Infosys Jobs into PostgreSQL!", flush=True)
    return inserted

if __name__ == "__main__":
    import_infosys_jobs()
