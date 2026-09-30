import sys
import logging
from datetime import datetime
import tracemalloc
from src.ats.registry import AtsRegistry
from src.ats.adapters import *
from src.dto.crawler_context import CrawlerContext
import requests

logging.basicConfig(level=logging.INFO)

COMPANIES = [
    {
        "name": "Micron",
        "id": "micron",
        "officialCareerPage": "https://micron.eightfold.ai/careers",
        "atsType": "EIGHTFOLD",
        "token": "micron.com" # Some Eightfold portals use domain for token
    },
    {
        "name": "Dexcom",
        "id": "dexcom",
        "officialCareerPage": "https://careers.eightfold.ai/dexcom",
        "atsType": "EIGHTFOLD",
        "token": "dexcom.com"
    },
    {
        "name": "Zoho Corp",
        "id": "zohocorp",
        "officialCareerPage": "https://zohocorp.zohorecruit.com/jobs/Careers",
        "atsType": "ZOHO_RECRUIT"
    }
]

def benchmark():
    tracemalloc.start()
    
    for config in COMPANIES:
        print(f"\n{'='*50}\nBenchmarking {config['name']} ({config['atsType']})\n{'='*50}")
        tracemalloc.reset_peak()
        
        CrawlerClass = AtsRegistry.get(config["atsType"])
        crawler = CrawlerClass(config)
        
        try:
            results = crawler.execute()
            
            current, peak = tracemalloc.get_traced_memory()
            peak_mb = peak / 10**6
            current_mb = current / 10**6
            
            print(f"\n[BENCHMARK RESULTS]")
            num_jobs = results['totalLiveJobs'] if isinstance(results, dict) and 'totalLiveJobs' in results else len(results)
            print(f"Total Live Jobs: {num_jobs}")
            
            duration = (crawler.end_time - crawler.start_time).total_seconds() if crawler.end_time else 0
            print(f"Execution Time : {duration:.2f} seconds")
            print(f"Peak Memory    : {peak_mb:.2f} MB")
            print(f"Current Memory : {current_mb:.2f} MB")
            
        except Exception as e:
            print(f"Failed: {e}")

if __name__ == "__main__":
    benchmark()
