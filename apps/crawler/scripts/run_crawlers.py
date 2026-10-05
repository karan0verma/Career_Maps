import os
import sys
import json
import logging

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
    
    logger.info("NOTE: Using Locked Architecture. Individual scripts must be run directly for specific companies.")
    logger.info("Skipping generic crawler execution because ATS adapters are decoupled.")

    with open(jobs_file, "w") as f:
        json.dump(all_jobs, f)
        
    logger.info(f"Exported total {len(all_jobs)} crawled jobs.")

if __name__ == '__main__':
    run_crawlers()
