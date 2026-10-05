import os
import sys
import json
import logging
from dataclasses import asdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.registry import CrawlerRegistry
import src.crawlers

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
        logger.info(f"--- Crawling {c['display_name']} ---")
        crawler_class = CrawlerRegistry.get_crawler(c['official_name'].lower()) or CrawlerRegistry.get_crawler(c['display_name'].lower())
        
        if not crawler_class:
            logger.warning(f"No crawler found for {c['display_name']}. Skipping.")
            continue

        try:
            crawler = crawler_class()
            crawler.company_id = c['company_id']
            context = crawler.execute()
            normalized_jobs = context.get("normalized_jobs", [])
            
            logger.info(f"Found {len(normalized_jobs)} jobs for {c['display_name']}.")
            for job in normalized_jobs:
                job_dict = asdict(job)
                job_dict['companyId'] = c['company_id']
                all_jobs.append(job_dict)

        except Exception as e:
            logger.error(f"Failed to crawl {c['display_name']}: {e}")

    with open(jobs_file, "w") as f:
        json.dump(all_jobs, f)
        
    logger.info(f"Exported total {len(all_jobs)} crawled jobs.")

if __name__ == '__main__':
    run_crawlers()
