import os
import sys
import re
import time
import logging
from datetime import datetime
import pdfplumber

# Setup paths
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from src.db.session import SessionLocal
from src.models.job import Job
from src.models.company import Company, CompanySource
from src.services.crawler import CrawlerService

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def ingest_and_crawl(pdf_path: str):
    db = SessionLocal()
    
    logger.info(f"Extracting text from {pdf_path}")
    
    companies_data = []
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() + '\n'
            
    lines = text.split('\n')
    for line in lines:
        if "Name (Company Name)" in line or not line.strip():
            continue
            
        urls = re.findall(r'(https?://[^\s]+)', line)
        if len(urls) >= 2:
            website = urls[0]
            career_url = urls[1]
            
            # Everything before the first URL is name + industry
            prefix = line.split(website)[0].strip()
            name = prefix # Just use the whole prefix as the company name to avoid complex parsing
            
            if name and career_url:
                companies_data.append({
                    "name": name,
                    "website": website,
                    "career_url": career_url
                })
    
    logger.info(f"Extracted {len(companies_data)} companies from PDF text.")
    
    successful_count = 0
    
    for i, data in enumerate(companies_data):
        # Insert or get company
        comp = db.query(Company).filter(Company.website == data['website']).first()
        if not comp:
            comp = db.query(Company).filter(Company.display_name == data['name']).first()
            
        if not comp:
            try:
                comp = Company(
                    official_name=data['name'],
                    display_name=data['name'],
                    industry="Unknown",
                    website=data['website'],
                    career_url=data['career_url'],
                    is_active=True
                )
                db.add(comp)
                db.commit()
                db.refresh(comp)
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to insert {data['name']}: {e}")
                continue
        else:
            # Update career url if missing
            try:
                if not comp.career_url or comp.career_url != data['career_url']:
                    comp.career_url = data['career_url']
                    db.commit()
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to update {data['name']}: {e}")
                
        # Setup source
        cached_source = db.query(CompanySource).filter(
            CompanySource.company_id == comp.company_id,
            CompanySource.health_status == 'ACTIVE'
        ).first()
        
        if not cached_source:
            db.add(CompanySource(
                company_id=comp.company_id, 
                source_url=data['career_url'], 
                extraction_strategy="", 
                health_status="ACTIVE",
                last_verified_at=datetime.utcnow()
            ))
            db.commit()
            
        # Run crawler
        try:
            from src.models.scheduler import CrawlHistory
            from datetime import timedelta
            
            recent_history = db.query(CrawlHistory).filter(
                CrawlHistory.company_id == comp.company_id,
                CrawlHistory.started_at > datetime.utcnow() - timedelta(days=30)
            ).first()
            
            if recent_history:
                logger.info(f"[{i+1}/{len(companies_data)}] Skipping {comp.display_name} - recently crawled.")
                continue
                
            logger.info(f"[{i+1}/{len(companies_data)}] Triggering crawler for {comp.display_name}")
            history = CrawlerService.run_crawl(db, comp.company_id, force_run=True)
            if history.status == "SUCCESS":
                successful_count += 1
            logger.info(f"Crawler finished with status: {history.status}")
        except Exception as e:
            logger.error(f"Crawling failed for {comp.display_name}: {e}")
            
    logger.info(f"Ingestion complete. Successfully extracted jobs for {successful_count} companies.")

if __name__ == "__main__":
    pdf_file = r"C:\Users\Ahana Singh\.gemini\antigravity\brain\b2157c5e-32e9-4e58-993a-3a6a43a0d53a\.user_uploaded\media_1786457520045.pdf"
    ingest_and_crawl(pdf_file)
