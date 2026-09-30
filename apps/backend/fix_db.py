import sys
import os
import requests
import json
import re
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.db.session import SessionLocal
from src.models.job import Job
from src.models.company import Company
from bs4 import BeautifulSoup

def fix_jobs():
    db = SessionLocal()
    
    # 1. Fix SmartRecruiters apply URLs
    print("Fixing SmartRecruiters URLs...")
    sr_jobs = db.query(Job).filter(Job.apply_url.like('%api.smartrecruiters.com%')).all()
    for job in sr_jobs:
        # e.g. https://api.smartrecruiters.com/v1/companies/unacademy/postings/743999710952745
        match = re.search(r'companies/([^/]+)/postings/([^/]+)', job.apply_url)
        if match:
            company_id = match.group(1)
            job_id = match.group(2)
            job.apply_url = f"https://jobs.smartrecruiters.com/{company_id}/{job_id}"
            
    db.commit()
    print(f"Fixed {len(sr_jobs)} SmartRecruiters apply_urls.")

    # 2. Fix missing descriptions (by hitting the ATS pages directly if possible)
    missing_desc_jobs = db.query(Job).filter(Job.description == None, Job.is_active == True).all()
    print(f"Found {len(missing_desc_jobs)} jobs with missing descriptions.")
    
    for job in missing_desc_jobs:
        if "smartrecruiters.com" in job.apply_url:
            # We can use the api endpoint to get description
            company_id = job.apply_url.split('/')[-2]
            job_id = job.apply_url.split('/')[-1].split('-')[0]
            api_url = f"https://api.smartrecruiters.com/v1/companies/{company_id}/postings/{job_id}"
            try:
                res = requests.get(api_url, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    job_ad = data.get("jobAd", {})
                    if job_ad and isinstance(job_ad.get("sections"), dict):
                        sections = job_ad["sections"]
                        desc = sections.get("jobDescription", {}).get("text", "")
                        qual = sections.get("qualifications", {}).get("text", "")
                        job.description = f"{desc}<br/><br/>{qual}"
            except Exception as e:
                print(f"Failed to fetch SR desc for {job_id}: {e}")
        else:
            # Try to fetch generic description from the page
            try:
                # We need a proper user agent
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                res = requests.get(job.apply_url, headers=headers, timeout=5)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    # Just grab all text from body for now as a fallback
                    text = soup.get_text(separator='<br/>', strip=True)
                    # Simple heuristic: Take middle 2000 chars as the description
                    if len(text) > 1000:
                        job.description = text[500:2500] + "..."
                    else:
                        job.description = text
            except:
                pass
                
    db.commit()
    print("Database patching complete.")

if __name__ == '__main__':
    fix_jobs()
