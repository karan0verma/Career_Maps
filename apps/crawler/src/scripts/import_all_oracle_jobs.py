import os
import sys
import uuid
import json
import time
import math
import urllib.request
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job

def import_oracle_india():
    print("=" * 80, flush=True)
    print("INGESTING ORACLE INDIA (224 VERIFIED LIVE JOBS)", flush=True)
    print("=" * 80, flush=True)

    db = SessionLocal()

    # 1. Company Record
    company = db.query(Company).filter(Company.display_name.ilike('%oracle%')).first()
    if not company:
        company = Company(
            company_id=uuid.uuid4(),
            official_name="Oracle India Private Limited",
            display_name="Oracle",
            website="https://www.oracle.com",
            career_url="https://careers.oracle.com/jobs/",
            company_size="100,000+",
            industry="Database, Cloud & Enterprise Software",
            headquarters="Bengaluru, Karnataka, India",
            is_active=True,
            logo_url="https://upload.wikimedia.org/wikipedia/commons/5/50/Oracle_logo.svg",
            country="India",
            city="Bengaluru"
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        print(f"Created Company record: {company.display_name} ({company.company_id})", flush=True)
    else:
        print(f"Using Existing Company: {company.display_name} ({company.company_id})", flush=True)

    # 2. Extract Oracle India jobs via Oracle Cloud Recruiting REST API
    PAGE_SIZE = 25
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://careers.oracle.com/'
    }

    base_url = "https://eeho.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.workLocation,requisitionList.otherWorkLocations,requisitionList.secondaryLocations,flexFieldsFacet.values,requisitionList.requisitionFlexFields&finder=findReqs;siteNumber=CX_45001,facetsList=LOCATIONS%3BTITLES,selectedLocationsFacet=300000000106947,sortBy=POSTING_DATES_DESC,limit="
    
    # Probe initial
    init_url = f"{base_url}{PAGE_SIZE},offset=0"
    req = urllib.request.Request(init_url, headers=headers)
    res = urllib.request.urlopen(req)
    d = json.loads(res.read().decode())
    item0 = d['items'][0]
    total_count = item0.get('TotalJobsCount', 224)
    print(f"Total Live Oracle India Jobs to Ingest: {total_count}", flush=True)

    all_requisitions = []
    all_requisitions.extend(item0.get('requisitionList', []))

    num_pages = math.ceil(total_count / PAGE_SIZE)
    for p in range(1, num_pages):
        offset = p * PAGE_SIZE
        page_url = f"{base_url}{PAGE_SIZE},offset={offset}"
        try:
            r = urllib.request.Request(page_url, headers=headers)
            resp = urllib.request.urlopen(r)
            data = json.loads(resp.read().decode())
            reqs = data['items'][0].get('requisitionList', [])
            all_requisitions.extend(reqs)
            print(f"  Fetched Oracle page {p+1}/{num_pages} ({len(all_requisitions)}/{total_count} jobs)...", flush=True)
            time.sleep(0.4)
        except Exception as e:
            print(f"  Error on page {p}: {e}", flush=True)

    print(f"\nTotal extracted Oracle requisitions: {len(all_requisitions)}", flush=True)

    # 3. Clean & Ingest into PostgreSQL
    db.query(Job).filter(Job.company_id == company.company_id).delete()
    db.commit()

    inserted = 0
    seen_urls = set()

    for r in all_requisitions:
        req_id = str(r.get('Id') or '')
        if not req_id:
            continue
        
        apply_url = f"https://careers.oracle.com/jobs/#en/sites/jobsearch/job/{req_id}"
        if apply_url in seen_urls:
            continue
        seen_urls.add(apply_url)

        title = r.get('Title', '').strip()
        location = r.get('PrimaryLocation', '').strip() or "India"
        workplace_type = r.get('WorkplaceType') or 'Hybrid'
        
        desc = r.get('ExternalDescriptionStr') or r.get('PostingDescription') or f"Oracle India is hiring for {title} in {location}."
        
        posted_date = None
        if r.get('PostedDate'):
            try:
                posted_date = datetime.fromisoformat(r.get('PostedDate').replace('Z', '+00:00'))
            except:
                pass

        job = Job(
            job_id=uuid.uuid4(),
            company_id=company.company_id,
            external_job_id=req_id,
            title=title,
            location=location,
            country="India",
            employment_type="Full-time",
            work_mode=workplace_type,
            description=desc,
            apply_url=apply_url,
            first_seen_at=posted_date or datetime.utcnow(),
            last_seen_at=datetime.utcnow(),
            is_active=True
        )
        db.add(job)
        inserted += 1

    db.commit()
    print(f"\nOracle Ingestion Complete:", flush=True)
    print(f"  • Inserted Live Positions: {inserted}", flush=True)
    total_db_jobs = db.query(Job).filter(Job.company_id == company.company_id, Job.is_active == True).count()
    print(f"  • Total Active Oracle India Jobs in DB: {total_db_jobs}", flush=True)
    db.close()

if __name__ == "__main__":
    import_oracle_india()
