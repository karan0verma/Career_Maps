import tracemalloc
import time
from typing import Dict, Any
from src.ats.registry import AtsRegistry
import logging

logging.basicConfig(level=logging.INFO)

def run_benchmark(company_name: str, ats_type: str, url: str) -> None:
    print(f"\n{'='*50}")
    print(f"Benchmarking {company_name} ({ats_type})")
    print(f"{'='*50}")
    
    config = {
        "id": f"test-{company_name.lower()}",
        "companyName": company_name,
        "officialCareerPage": url,
        "opportunities": []
    }
    
    crawler_class = AtsRegistry.get(ats_type)
    if not crawler_class:
        print(f"Adapter for {ats_type} not found.")
        return
        
    tracemalloc.start()
    start_time = time.time()
    
    crawler = crawler_class(config)
    result = crawler.execute()
    
    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print("\n[BENCHMARK RESULTS]")
    print(f"Total Live Jobs: {result.get('totalLiveJobs', 0)}")
    print(f"Execution Time : {end_time - start_time:.2f} seconds")
    print(f"Peak Memory    : {peak / 10**6:.2f} MB")
    print(f"Current Memory : {current / 10**6:.2f} MB")

if __name__ == "__main__":
    AtsRegistry.load_adapters()
    
    # Ashby Tests
    run_benchmark("Reddit", "ASHBY", "https://jobs.ashbyhq.com/reddit")
    run_benchmark("Vanta", "ASHBY", "https://jobs.ashbyhq.com/vanta")
    run_benchmark("Notion", "ASHBY", "https://jobs.ashbyhq.com/notion")
    
    # SmartRecruiters Tests
    run_benchmark("Visa", "SMARTRECRUITERS", "https://careers.smartrecruiters.com/visa")
    run_benchmark("Roblox", "SMARTRECRUITERS", "https://careers.smartrecruiters.com/roblox")
    run_benchmark("Ubisoft", "SMARTRECRUITERS", "https://careers.smartrecruiters.com/ubisoft")
    
    # Workable Tests
    run_benchmark("Eurobank", "WORKABLE", "https://apply.workable.com/eurobank")
    run_benchmark("Turing", "WORKABLE", "https://apply.workable.com/turing")
    run_benchmark("Mable", "WORKABLE", "https://apply.workable.com/mable")
