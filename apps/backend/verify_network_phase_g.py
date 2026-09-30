import sys
import os
import json
import time

from src.db.session import SessionLocal
from src.models.company import Company, CompanySource, CompanyATSHistory
from src.models.job import Job
from src.services.crawler import CrawlerService
import subprocess

original_run = subprocess.run

benchmark_results = {}
current_domain = None

def mock_run(*args, **kwargs):
    result = original_run(*args, **kwargs)
    try:
        lines = result.stdout.strip().split('\n')
        for line in reversed(lines):
            if line.startswith('{'):
                payload = json.loads(line)
                target = payload.get("target", {})
                val = target.get("metadata", {}).get("validation", {})
                if current_domain:
                    benchmark_results[current_domain]["raw"] = val.get("raw_count", 0)
                    benchmark_results[current_domain]["valid"] = val.get("valid_count", 0)
                    benchmark_results[current_domain]["rejected"] = val.get("rejected_count", 0)
                    benchmark_results[current_domain]["duplicates"] = val.get("duplicates_count", 0)
                    benchmark_results[current_domain]["strategy"] = target.get("extraction_strategy")
                    benchmark_results[current_domain]["ats"] = target.get("ats_type")
                break
    except Exception:
        pass
    return result

subprocess.run = mock_run

targets = [
    {"category": "Known ATS", "domain": "wipro.com", "career_url": "https://careers.wipro.com/"},
    {"category": "Known ATS", "domain": "paytm.com", "career_url": "https://jobs.lever.co/paytm"},
    {"category": "Custom", "domain": "tcs.com", "career_url": "https://www.tcs.com/careers"},
    {"category": "Custom", "domain": "globallogic.com", "career_url": "https://www.globallogic.com/careers/"},
    {"category": "Custom", "domain": "maqsoftware.com", "career_url": "https://maqsoftware.com/careers"},
    {"category": "Generic", "domain": "netflix.com", "career_url": "https://jobs.netflix.com/"},
    {"category": "Generic", "domain": "apple.com", "career_url": "https://jobs.apple.com/"},
    {"category": "Government", "domain": "usajobs.gov", "career_url": "https://www.usajobs.gov/Search/Results"}
]

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

print("--- Starting Phase G Benchmark (Universal Network/API Discovery) ---")

for t in targets:
    domain = t["domain"]
    url = t["career_url"]
    current_domain = domain
    benchmark_results[domain] = {}
    
    print(f"\n[{t['category']}] Evaluating: {domain}")
    
    company = ensure_company(domain, url)
    
    # Clear cache
    db.query(CompanySource).filter(CompanySource.company_id == company.company_id).delete()
    db.query(CompanyATSHistory).filter(CompanyATSHistory.company_id == company.company_id).delete()
    db.query(Job).filter(Job.company_id == company.company_id).delete()
    db.commit()
    
    start_time = time.time()
    hist1 = CrawlerService.run_crawl(db, company.company_id)
    dur1 = time.time() - start_time
    
    db_jobs = db.query(Job).filter(Job.company_id == company.company_id).count()
    sources = db.query(CompanySource).filter(CompanySource.company_id == company.company_id).all()
    
    res = benchmark_results[domain]
    res["run1_time"] = dur1
    res["run1_status"] = hist1.status
    res["db_jobs"] = db_jobs
    res["cache_created"] = len(sources) > 0
    if len(sources) > 0:
        res["cached_url"] = sources[0].source_url
    
    print(f"Run 1: {dur1:.2f}s | Status: {hist1.status} | Strategy: {res.get('strategy')} | DB Jobs: {db_jobs} | Cached: {res['cache_created']}")
    
    # Cache Run 2 if eligible
    if db_jobs > 0:
        print("  -> Performing Cache Hit Test (Run 2)")
        start_time2 = time.time()
        hist2 = CrawlerService.run_crawl(db, company.company_id)
        dur2 = time.time() - start_time2
        res["run2_time"] = dur2
        res["cache_time_diff"] = dur1 - dur2
        print(f"  -> Run 2: {dur2:.2f}s (Speedup: {dur1 - dur2:.2f}s)")
        
print("\n--- Benchmark Complete. Generating JSON ---")
with open("phase_g_results.json", "w") as f:
    json.dump(benchmark_results, f, indent=2)
print("Saved to phase_g_results.json")
