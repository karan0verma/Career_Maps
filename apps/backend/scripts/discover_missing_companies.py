import os
import sys
import time
import logging
from datetime import datetime

# Setup paths
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from src.db.session import SessionLocal
from src.models.job import Job
from src.models.company import Company, CompanySource
from src.services.crawler import CrawlerService
from sqlalchemy import select

from duckduckgo_search import DDGS

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def run_discovery():
    db = SessionLocal()
    
    # Get companies without active jobs
    active_job_companies_subq = select(Job.company_id).filter(Job.is_active==True, Job.is_deleted==False).distinct()
    empty_companies = db.query(Company).filter(
        ~Company.company_id.in_(active_job_companies_subq), 
        Company.is_active==True, 
        Company.is_deleted==False
    ).all()
    
    ddgs = DDGS()
    
    logger.info(f"Starting discovery for {len(empty_companies)} companies.")
    
    successful_count = 0
    
    for i, comp in enumerate(empty_companies):
        logger.info(f"[{i+1}/{len(empty_companies)}] Processing {comp.display_name}...")
        
        # 1. Search for career URL if missing
        career_url = comp.career_url
        if not career_url:
            query = f"{comp.display_name} careers jobs"
            try:
                logger.info(f"Searching DuckDuckGo for: {query}")
                results = list(ddgs.text(query, max_results=3))
                if results:
                    career_url = results[0]['href']
                    logger.info(f"Found URL: {career_url}")
                    comp.career_url = career_url
                    db.commit()
                else:
                    logger.warning(f"No search results for {comp.display_name}")
                    continue
            except Exception as e:
                logger.error(f"Search failed for {comp.display_name}: {e}")
                time.sleep(2) # Backoff on error
                continue
                
            time.sleep(1) # Polite delay
            
        # 2. Add CompanySource so CrawlerService passes the URL
        cached_source = db.query(CompanySource).filter(
            CompanySource.company_id == comp.company_id,
            CompanySource.health_status == 'ACTIVE'
        ).first()
        
        if not cached_source and career_url:
            db.add(CompanySource(
                company_id=comp.company_id, 
                source_url=career_url, 
                extraction_strategy="", # Empty string bypasses not-null and makes run_single.py use None
                health_status="ACTIVE",
                last_verified_at=datetime.utcnow()
            ))
            db.commit()
            
        # 3. Trigger Crawler
        try:
            logger.info(f"Triggering crawler for {comp.display_name}")
            history = CrawlerService.run_crawl(db, comp.company_id, force_run=True)
            successful_count += 1
            logger.info(f"Crawler finished with status: {history.status}")
        except Exception as e:
            logger.error(f"Crawling failed for {comp.display_name}: {e}")
            
    logger.info(f"Discovery complete. Successfully ran crawler for {successful_count} companies.")

if __name__ == "__main__":
    run_discovery()
