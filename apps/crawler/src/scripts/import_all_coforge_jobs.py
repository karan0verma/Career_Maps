import sys
import os
import json
import uuid
import re
import datetime
from uuid import UUID
import requests
from bs4 import BeautifulSoup

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job

def clean_html_description(html_text: str) -> str:
    if not html_text:
        return ""
    # Replace breaks and paragraphs with newlines
    text = html_text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
    text = text.replace('</p>', '\n\n').replace('</li>', '\n')
    soup = BeautifulSoup(text, 'html.parser')
    clean = soup.get_text()
    # Normalize multiple newlines
    clean = re.sub(r'\n{3,}', '\n\n', clean)
    return clean.strip()

def import_coforge_jobs():
    print("=" * 70)
    print("STARTING LIVE EXTRACTION & INGESTION FOR COFORGE (99 JOBS)")
    print("=" * 70)
    
    url = 'https://public.zwayam.com/jobs/search'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Origin': 'https://careers.coforge.com',
        'Referer': 'https://careers.coforge.com/coforge/'
    }

    all_raw_jobs = []
    start = 0

    while True:
        d = {
            'filterCri': json.dumps({
                'paginationStartNo': start,
                'selectedCall': 'sort',
                'sortCriteria': {
                    'name': 'modifiedDate',
                    'isAscending': False
                },
                'anyOfTheseWords': ''
            }),
            'domain': 'careers.coforge.com',
            'companyId': 'MTUxNzM='
        }
        r = requests.post(url, headers=headers, data=d, timeout=15)
        if r.status_code != 200:
            print(f"Error fetching batch at start={start}: {r.status_code}")
            break
        items = r.json().get('data', {}).get('data', [])
        if not items:
            break
        all_raw_jobs.extend(items)
        print(f"Fetched batch at start={start}: {len(items)} jobs (Total: {len(all_raw_jobs)})")
        if len(items) < 10:
            break
        start += len(items)

    print(f"\nTotal raw jobs extracted from live portal: {len(all_raw_jobs)}")
    
    db = SessionLocal()
    
    # 1. Target Coforge company in DB
    coforge = db.query(Company).filter(Company.company_id == UUID('af7bc651-d0b4-400f-8d57-9eb76636b11d')).first()
    if not coforge:
        coforge = db.query(Company).filter(Company.display_name == 'Coforge').first()
    if not coforge:
        print("ERROR: Coforge company record not found in database!")
        db.close()
        return

    print(f"Assigning jobs to Company: {coforge.display_name} (ID: {coforge.company_id})")
    
    # Deactivate any legacy/stale records for Coforge
    db.query(Job).filter(Job.company_id == coforge.company_id).delete()
    db.commit()
    print("Cleaned previous jobs for Coforge.")

    inserted_count = 0
    seen_urls = set()

    for item in all_raw_jobs:
        src = item.get('_source', item)
        job_ext_id = str(src.get('id') or item.get('_id'))
        title = src.get('jobTitle') or src.get('designation') or src.get('roles') or "Software Engineer"
        title = title.strip()
        
        slug = src.get('jobUrl') or f"job-{job_ext_id}"
        apply_url = f"https://careers.coforge.com/coforge/jobview/{slug}?id={job_ext_id}"
        
        if apply_url in seen_urls:
            continue
        seen_urls.add(apply_url)
        
        # Location mapping
        loc_records = src.get('jobLocationRecord', [])
        if loc_records and isinstance(loc_records, list) and len(loc_records) > 0:
            city = loc_records[0].get('city') or src.get('location') or 'Global'
            country = loc_records[0].get('country') or 'India'
            location = loc_records[0].get('formattedLocation') or f"{city}, {country}"
        else:
            city = src.get('location') or 'Global'
            country = 'India' if any(c in city.lower() for c in ['noida', 'hyderabad', 'bangalore', 'bengaluru', 'mumbai', 'pune', 'chennai', 'gurgaon', 'kolkata']) else 'International'
            location = f"{city}, {country}"

        # Experience
        exp = src.get('yrsOfExperience')
        if not exp and src.get('minYrsOfExperience'):
            exp = f"{src.get('minYrsOfExperience')} Years"
        if exp:
            exp = exp.strip()

        # Skills
        raw_skills = src.get('mandatorySkills') or []
        if not raw_skills and src.get('jdSkillsKnownList'):
            raw_skills = src.get('jdSkillsKnownList')[:6]
        
        cleaned_skills = []
        for s in raw_skills:
            if s and isinstance(s, str) and len(s.strip()) > 1 and s.lower() != 'null':
                cleaned_skills.append(s.strip())

        # Work Mode
        work_mode = src.get('workMode') or "On-site / Hybrid"

        # Description
        raw_desc = src.get('shortDescription') or ""
        clean_desc = clean_html_description(raw_desc)
        
        if not clean_desc or len(clean_desc) < 20:
            skill_str = ", ".join(cleaned_skills) if cleaned_skills else "Software Engineering"
            clean_desc = f"Coforge is hiring for the position of {title} located in {location}.\n\nKey Qualifications & Skills:\n• Primary Skills: {skill_str}\n• Experience: {exp or 'Relevant experience in industry standards'}\n• Domain: {src.get('departmentName') or 'Technology Services'}\n\nInterested candidates can apply directly through the official career link below."

        job = Job(
            job_id=uuid.uuid4(),
            company_id=coforge.company_id,
            title=title,
            location=location,
            city=city,
            country=country,
            work_mode=work_mode,
            employment_type="Full-time",
            experience_level=exp,
            required_skills=cleaned_skills,
            description=clean_desc,
            requirements=f"Experience: {exp} | Skills: {', '.join(cleaned_skills)}",
            apply_url=apply_url,
            is_active=True,
            is_deleted=False,
            first_seen_at=datetime.datetime.now(datetime.timezone.utc),
            last_seen_at=datetime.datetime.now(datetime.timezone.utc)
        )
        db.add(job)
        inserted_count += 1

    db.commit()
    print(f"\nSuccessfully committed {inserted_count} jobs to PostgreSQL!")

    # Verify DB count
    total_in_db = db.query(Job).filter(Job.company_id == coforge.company_id, Job.is_active == True, Job.is_deleted == False).count()
    print(f"VERIFIED DATABASE COUNT FOR COFORGE: {total_in_db} jobs")
    db.close()

if __name__ == "__main__":
    import_coforge_jobs()
