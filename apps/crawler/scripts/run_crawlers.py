import os
import sys
import json
import logging
from dataclasses import asdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.universal_crawler import UniversalCrawler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_crawlers():
    companies_file = "active_companies.json"
    jobs_file = "daily_jobs.json"
    
    if not os.path.exists(companies_file):
        logger.error(f"{companies_file} not found!")
        return

    with open(companies_file, "r") as f:
        companies = json.load(f)

    all_jobs = []
    
    for c in companies:
        logger.info(f"--- Crawling {c['display_name']} with Universal Engine ---")
        
        try:
            # BaseCrawler expects: id, companyName, officialCareerPage
            company_data = {
                "id": c['company_id'],
                "companyName": c['display_name'],
                "officialName": c['official_name'],
                "officialCareerPage": c.get("career_url") or f"https://www.{c['official_name']}.com/careers",
                "website": c.get("website") or f"https://www.{c['official_name']}.com"
            }
            
            crawler = UniversalCrawler(company_data)
            context = crawler.execute()
            normalized_jobs = context.get("normalized_jobs", [])
            
            logger.info(f"Found {len(normalized_jobs)} jobs for {c['display_name']}.")
            for job in normalized_jobs:
                try:
                    job_dict = asdict(job)
                except TypeError:
                    job_dict = job if isinstance(job, dict) else job.__dict__
                job_dict['companyId'] = c['company_id']
                all_jobs.append(job_dict)

        except Exception as e:
            logger.error(f"Failed to crawl {c['display_name']}: {e}")

    with open(jobs_file, "w") as f:
        json.dump(all_jobs, f)
        
    logger.info(f"Exported total {len(all_jobs)} crawled jobs.")

if __name__ == '__main__':
    run_crawlers()
