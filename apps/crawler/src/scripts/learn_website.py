import sys
import os
import time
import json
import logging
import argparse
from typing import Dict, Any

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
backend_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env'))
load_dotenv(backend_env_path)

from src.db.session import SessionLocal
from src.models.company import Company, CompanySource
from src.models.job import Job
from src.discovery.network_interceptor import NetworkInterceptor
from src.discovery.response_scorer import ResponseScorer
from src.extractors.api_extractor import APIExtractor
from src.validators.job_validator import JobValidator
from src.dto.crawler_context import CrawlerContext

from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def run_learning_session(company: Company) -> Dict[str, Any]:
    print(f"\n[{company.display_name}] Launching learning session for: {company.career_url}")
    print("Please wait while Playwright opens the browser...")
    
    captured_responses = []
    
    def handle_response(response):
        if response.status >= 400 or response.request.method == "OPTIONS":
            return
        
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return
            
        url = response.url
        ignore_kws = ["analytics", "tracking", "telemetry", "google", "facebook", "fonts", "css"]
        if any(kw in url.lower() for kw in ignore_kws):
            return
            
        try:
            body = response.json()
            score, job_list = ResponseScorer.score_response(body)
            if score > 5:
                captured_responses.append({
                    "url": url,
                    "method": response.request.method,
                    "score": score,
                    "body": body,
                    "jobs": job_list
                })
        except:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.on("response", handle_response)
        
        try:
            page.goto(company.career_url)
        except Exception as e:
            print(f"Failed to load URL: {e}")
            
        print("\n" + "="*50)
        print("BROWSER IS OPEN.")
        print("Please interact with the website (search jobs, scroll, click next page).")
        print("When you are finished, press ENTER here in the terminal to analyze.")
        print("="*50 + "\n")
        
        input()
        browser.close()
        
    return captured_responses

def generate_extraction_config(responses: list) -> Dict[str, Any]:
    if not responses:
        return None
        
    # Pick the best response
    best = sorted(responses, key=lambda x: x['score'], reverse=True)[0]
    
    # Deterministically build the config
    config = {
        "api_url": best["url"],
        "method": best["method"],
        "jobs_path": "", 
        "field_mapping": {}
    }
    
    # Simple mapping using existing rules
    if best["jobs"] and len(best["jobs"]) > 0:
        sample = best["jobs"][0]
        keys = list(sample.keys()) if isinstance(sample, dict) else []
        
        for k in keys:
            kl = str(k).lower()
            if any(s in kl for s in ResponseScorer.JOB_SIGNALS['title']):
                config["field_mapping"]["title"] = k
            elif any(s in kl for s in ResponseScorer.JOB_SIGNALS['id']):
                config["field_mapping"]["external_job_id"] = k
            elif any(s in kl for s in ResponseScorer.JOB_SIGNALS['location']):
                config["field_mapping"]["location"] = k
            elif any(s in kl for s in ResponseScorer.JOB_SIGNALS['description']):
                config["field_mapping"]["description"] = k
            elif any(s in kl for s in ResponseScorer.JOB_SIGNALS['url']):
                config["field_mapping"]["apply_url"] = k

    return config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--company", required=False, help="Company Name")
    parser.add_argument("--company-id", required=False, help="Company ID")
    args = parser.parse_args()
    
    if not args.company and not args.company_id:
        print("Error: Must provide --company or --company-id")
        return
        
    # Setup DB path manually if running standalone
    db = SessionLocal()
    if args.company_id:
        company = db.query(Company).filter(Company.company_id == args.company_id).first()
    else:
        company = db.query(Company).filter(Company.display_name.ilike(f"%{args.company}%")).first()
    
    if not company:
        print(f"Company {args.company} not found in database.")
        return
        
    responses = run_learning_session(company)
    print(f"\nCollected {len(responses)} high-signal JSON responses.")
    
    config = generate_extraction_config(responses)
    if not config:
        print("Could not reliably learn this career website.")
        return
        
    print("\nGenerated Config:")
    print(json.dumps(config, indent=2))
    
    import requests
    class MockContext:
        session = requests.Session()
    
    company_dict = {
        "company_id": str(company.company_id),
        "display_name": company.display_name,
        "metadata": {"extraction_config": config, "discovered_api_url": config["api_url"]}
    }
    
    extractor = APIExtractor(company.display_name, company_dict)
    
    print("\nExtracting jobs using new config...")
    jobs_raw = extractor.crawl(MockContext())
    
    valid_jobs = []
    validator = JobValidator()
    for raw in jobs_raw:
        is_valid, errors, normalized = validator.validate(raw, str(company.company_id), company.display_name)
        if is_valid:
            valid_jobs.append(normalized)
            
    print(f"\nDiscovered jobs: {len(jobs_raw)}")
    print(f"Valid jobs: {len(valid_jobs)}")
    print(f"Invalid jobs: {len(jobs_raw) - len(valid_jobs)}")
    
    if len(valid_jobs) == 0:
        print("Could not reliably learn this career website. (0 valid jobs)")
        return
        
    # Save to CompanySource
    existing_source = db.query(CompanySource).filter(CompanySource.company_id == company.company_id).first()
    if existing_source:
        existing_source.extraction_strategy = "COMPANY_WEBSITE_LEARNED"
        existing_source.extraction_config = config
    else:
        new_source = CompanySource(
            company_id=company.company_id,
            source_url=company.career_url,
            extraction_strategy="COMPANY_WEBSITE_LEARNED",
            extraction_config=config,
            health_status="ACTIVE"
        )
        db.add(new_source)
        
    # We do NOT insert into PostgreSQL here because that would bypass the main pipeline 
    # but the prompt says: "insert/update real jobs in PostgreSQL". 
    # Let's insert them for the first run, and the second run will use standard pipeline.
    for j in valid_jobs:
        new_job = Job(**j.dict())
        db.add(new_job)
        
    db.commit()
    
    print("\n" + "="*50)
    print(f"Company: {company.display_name}")
    print(f"Source discovered: {config['api_url']}")
    print(f"Raw jobs discovered: {len(jobs_raw)}")
    print(f"Valid jobs: {len(valid_jobs)}")
    print(f"Invalid jobs: {len(jobs_raw) - len(valid_jobs)}")
    print(f"Jobs inserted: {len(valid_jobs)}")
    print(f"Extraction strategy: COMPANY_WEBSITE_LEARNED")
    print(f"LLM calls: 0")
    print("="*50)

if __name__ == "__main__":
    main()
