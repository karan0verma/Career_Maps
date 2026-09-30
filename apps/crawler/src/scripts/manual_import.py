import os
import sys
import json
import argparse
from datetime import datetime

# Setup paths to ensure we can import backend models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
backend_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env'))
load_dotenv(backend_env_path)

from src.db.session import SessionLocal
from src.models.company import Company, CompanySource
from src.models.job import Job
from src.utils.ai_schema_builder import AISchemaBuilder
from src.validators.job_validator import JobValidator

from playwright.sync_api import sync_playwright

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--company-id", required=True, help="Company ID")
    args = parser.parse_args()
    
    db = SessionLocal()
    company = db.query(Company).filter(Company.company_id == args.company_id).first()
    
    if not company:
        print(f"Company {args.company_id} not found in database.")
        return
        
    print(f"Starting Manual Import Session for: {company.display_name}")
    print(f"Target URL: {company.career_url}")
    print("\n" + "="*50)
    print("INSTRUCTIONS:")
    print("1. A browser window will open shortly.")
    print("2. Navigate to the job listings page, apply any filters, and ensure the jobs are visible.")
    print("3. DO NOT close the browser window yourself.")
    print("4. When you are ready to import, simply press ENTER in this terminal (the script will close the browser for you).")
    print("="*50 + "\n")
    
    captured_json = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Intercept JSON requests
        def handle_response(response):
            if "application/json" in response.headers.get("content-type", ""):
                try:
                    payload = response.json()
                    # Store only reasonable sized payloads
                    if len(str(payload)) < 50000:
                        captured_json.append(payload)
                except:
                    pass
                    
        page.on("response", handle_response)
        
        try:
            page.goto(company.career_url)
        except:
            pass # ignore initial navigation errors
            
        input("Press ENTER when jobs are visible on the screen...")
        
        print("\nExtracting evidence from page...")
        current_url = page.url
        
        try:
            # page.content() is more robust than page.evaluate for full DOM
            html_content = page.content()
        except Exception as e:
            print(f"Warning: Failed to get full content, retrying... ({e})")
            page.wait_for_timeout(1000)
            html_content = page.content()
            
        browser.close()
        
    print("Sending evidence to AI Schema Builder...")
    builder = AISchemaBuilder()
    result = builder.generate_schema({
        "html": html_content,
        "json_responses": captured_json
    })
    
    extracted_jobs = result.get("jobs", [])
    config = result.get("config", {})
    
    if not extracted_jobs:
        print("AI could not extract any jobs from the page.")
        return
        
    print(f"\nAI found {len(extracted_jobs)} raw jobs.")
    print(f"AI generated config: {json.dumps(config, indent=2)}")
    
    validator = JobValidator()
    valid_jobs = []
    duplicate_count = 0
    
    for j in extracted_jobs:
        j['company_id'] = company.company_id
        j['company_name'] = company.display_name
        # normalize
        valid, msg, dto = validator.validate(j)
        if valid:
            # Check for duplicate
            is_dup = db.query(Job).filter(
                Job.company_id == dto.companyId,
                Job.external_job_id == dto.externalJobId,
                Job.apply_url == dto.applyUrl
            ).first()
            if is_dup:
                duplicate_count += 1
            else:
                valid_jobs.append(dto)
            
    print("\n" + "="*50)
    print(f"Jobs found: {len(extracted_jobs)}")
    print(f"Valid jobs: {len(valid_jobs)}")
    print(f"Duplicate jobs: {duplicate_count}")
    print("="*50)
    
    if not valid_jobs:
        print("No valid jobs to import.")
        return
        
    confirm = input(f"\nImport {len(valid_jobs)} jobs and save this configuration for future daily crawls? (y/n): ")
    if confirm.lower() != 'y':
        print("Import cancelled.")
        return
        
    # Insert Jobs
    from sqlalchemy.dialects.postgresql import insert
    for j in valid_jobs:
        job_dict = j.dict()
        # Ensure enums are handled if needed by model (Job uses String in db)
        stmt = insert(Job).values(**job_dict)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=['company_id', 'external_job_id', 'apply_url']
        )
        db.execute(stmt)
        
    # Save Source
    strategy = "GENERIC_DOM" if config.get("source_type") == "DOM" else "GENERIC_API"
    config['source_url'] = current_url
    
    existing_source = db.query(CompanySource).filter(CompanySource.company_id == company.company_id).first()
    if existing_source:
        existing_source.extraction_strategy = strategy
        existing_source.extraction_config = config
        existing_source.source_url = current_url
        existing_source.last_successful_crawl = datetime.utcnow()
    else:
        new_source = CompanySource(
            company_id=company.company_id,
            source_url=current_url,
            extraction_strategy=strategy,
            extraction_config=config,
            health_status="ACTIVE",
            last_successful_crawl=datetime.utcnow()
        )
        db.add(new_source)
        
    db.commit()
    print("Jobs imported and source saved successfully!")

if __name__ == "__main__":
    main()
