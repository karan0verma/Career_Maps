import sys
import os
import json
import time
import subprocess

from src.db.session import SessionLocal
from src.models.company import Company, CompanySource, CompanyATSHistory
from src.models.job import Job
from src.services.crawler import CrawlerService

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
                meta = target.get("metadata", {})
                if current_domain:
                    benchmark_results[current_domain]["raw"] = val.get("raw_count", 0)
                    benchmark_results[current_domain]["valid"] = val.get("valid_count", 0)
                    benchmark_results[current_domain]["rejected"] = val.get("rejected_count", 0)
                    benchmark_results[current_domain]["duplicates"] = val.get("duplicates_count", 0)
                    benchmark_results[current_domain]["strategy"] = target.get("extraction_strategy")
                    benchmark_results[current_domain]["llm_nav_used"] = meta.get("llm_nav_used", False)
                    benchmark_results[current_domain]["llm_map_used"] = meta.get("llm_map_used", False)
                    
                    config = meta.get("extraction_config", {})
                    if config:
                        benchmark_results[current_domain]["api_url"] = config.get("api_url")
                        benchmark_results[current_domain]["schema_mapped"] = True
                        benchmark_results[current_domain]["is_mock"] = config.get("is_mock", False)
                break
    except Exception as e:
        pass
    return result

subprocess.run = mock_run

targets = [
    {"domain": "wipro.com", "url": "https://careers.wipro.com/"},
    {"domain": "paytm.com", "url": "https://jobs.lever.co/paytm"},
    {"domain": "apple.com", "url": "https://jobs.apple.com/"},
    {"domain": "netflix.com", "url": "https://jobs.netflix.com/"},
    {"domain": "tcs.com", "url": "https://www.tcs.com/careers"},
    {"domain": "globallogic.com", "url": "https://www.globallogic.com/careers/"},
    {"domain": "maqsoftware.com", "url": "https://maqsoftware.com/careers"},
    {"domain": "usajobs.gov", "url": "https://www.usajobs.gov/Search/Results"}
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

print("--- Starting Phase H Benchmark (LLM Discovery & Mappings) ---")

for t in targets:
    domain = t["domain"]
    url = t["url"]
    current_domain = domain
    benchmark_results[domain] = {}
    
    print(f"\nEvaluating: {domain}")
    
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
    res["db_jobs"] = db_jobs
    res["cache_created"] = len(sources) > 0
    
    print(f"Run 1: {dur1:.2f}s | Strategy: {res.get('strategy')} | DB Jobs: {db_jobs} | Schema Mapped: {res.get('schema_mapped', False)} | Is Mock LLM: {res.get('is_mock', False)}")
    
    # Cache Run 2
    if db_jobs > 0:
        print("  -> Performing Cache Hit Test (Run 2)")
        start_time2 = time.time()
        
        # Reset LLM counters for run 2
        res["run2_llm_nav_used"] = False
        res["run2_llm_map_used"] = False
        
        hist2 = CrawlerService.run_crawl(db, company.company_id)
        dur2 = time.time() - start_time2
        
        # Check run 2 output
        # mock_run will update current_domain again, so we'll see if llm_nav_used or llm_map_used got set to True
        llm_called_run2 = benchmark_results[domain].get("llm_nav_used") or benchmark_results[domain].get("llm_map_used")
        
        res["run2_time"] = dur2
        res["llm_called_run2"] = llm_called_run2
        print(f"  -> Run 2: {dur2:.2f}s | LLM Called: {llm_called_run2}")

print("\n--- Benchmark Complete ---")
with open("phase_h_results.json", "w") as f:
    json.dump(benchmark_results, f, indent=2)
print("Saved to phase_h_results.json")
