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
        "name": "Fivetran",
        "id": "fivetran",
        "officialCareerPage": "https://jobs.jobvite.com/fivetran",
        "atsType": "JOBVITE",
        # Providing the hash manually just in case HTML parsing fails on their SPA
        "token": "qyV9VfwP" 
    },
    {
        "name": "Universal Music",
        "id": "universalmusic",
        "officialCareerPage": "https://jobs.jobvite.com/universalmusicgroup",
        "atsType": "JOBVITE",
        "token": "q549Vfw0" # Example hash
    },
    {
        "name": "Asana",
        "id": "asana",
        "officialCareerPage": "https://asana.bamboohr.com/careers",
        "atsType": "BAMBOOHR"
    },
    {
        "name": "Wix",
        "id": "wix",
        "officialCareerPage": "https://wix.bamboohr.com/careers",
        "atsType": "BAMBOOHR"
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
            print(f"Total Live Jobs: {len(results)}")
            duration = (crawler.end_time - crawler.start_time).total_seconds() if crawler.end_time else 0
            print(f"Execution Time : {duration:.2f} seconds")
            print(f"Peak Memory    : {peak_mb:.2f} MB")
            print(f"Current Memory : {current_mb:.2f} MB")
            
            if results:
                print(f"Sample output keys: {list(results[0].model_dump().keys())}")
        except Exception as e:
            print(f"Failed: {e}")

if __name__ == "__main__":
    benchmark()
