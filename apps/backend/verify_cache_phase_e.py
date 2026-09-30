import sys
import os
import json
from uuid import uuid4
import time

from src.db.session import SessionLocal
from src.models.company import Company, CompanySource, CompanyATSHistory
from src.services.crawler import CrawlerService

targets = [
    {"domain": "wipro.com", "career_url": "https://careers.wipro.com/careers-home/"},
    {"domain": "tcs.com", "career_url": "https://www.tcs.com/careers"},
]

print("--- Real World Verification Phase E (Source Caching) ---")

db = SessionLocal()

def ensure_company(domain, career_url):
    c = db.query(Company).filter(Company.website == domain).first()
    if not c:
        c = Company(
            official_name=domain.split('.')[0].capitalize(),
            display_name=domain.split('.')[0].capitalize(),
            website=domain,
            career_url=career_url
        )
        db.add(c)
        db.commit()
        db.refresh(c)
    return c

for t in targets:
    domain = t["domain"]
    url = t["career_url"]
    print(f"\n--- Evaluating: {domain} ---")
    
    company = ensure_company(domain, url)
    
    # 1. Clear any existing sources to force discovery
    db.query(CompanySource).filter(CompanySource.company_id == company.company_id).delete()
    db.query(CompanyATSHistory).filter(CompanyATSHistory.company_id == company.company_id).delete()
    db.commit()
    
    print("\n[First Crawl - Forcing Discovery]")
    start_time = time.time()
    hist1 = CrawlerService.run_crawl(db, company.company_id)
    dur1 = time.time() - start_time
    print(f"Crawl finished in {dur1:.2f}s with status: {hist1.status}")
    print(f"Jobs found: {hist1.jobs_found}")
    
    # Verify DB Cache
    sources = db.query(CompanySource).filter(CompanySource.company_id == company.company_id).all()
    print(f"Sources cached: {len(sources)}")
    if sources:
        print(f"Cached Strategy: {sources[0].extraction_strategy}")
        print(f"Cached URL: {sources[0].source_url}")
        print(f"Cached Health: {sources[0].health_status}")
        
    print("\n[Second Crawl - Expecting Cache Hit]")
    start_time = time.time()
    hist2 = CrawlerService.run_crawl(db, company.company_id)
    dur2 = time.time() - start_time
    print(f"Crawl finished in {dur2:.2f}s with status: {hist2.status}")
    print(f"Jobs found: {hist2.jobs_found}")
    
    if dur2 < (dur1 * 0.7) and sources and sources[0].health_status == "ACTIVE":
        print(f"CACHE HIT SUCCESSFUL! Second crawl was {(dur1-dur2):.2f}s faster because discovery was skipped.")
    else:
        print("Note: Cache might not have been hit or overhead was similar. Check logs.")

