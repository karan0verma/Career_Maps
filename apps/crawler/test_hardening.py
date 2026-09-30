import tracemalloc
import time
from typing import Dict, Any
from src.ats.registry import AtsRegistry

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
    
    if result.get("totalLiveJobs", 0) > 0 and result.get("newOpportunities"):
        sample = result["newOpportunities"][0]
        # In the simulated chunking, newOpportunities might be [None] * size to save memory
        if sample:
            print(f"Sample DTO Field Check -> dept: {sample.get('department')}, workplace: {sample.get('workplaceType')}, published: {sample.get('publishedAt')}")
        else:
            print("Sample DTO check skipped (chunking enabled).")

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    AtsRegistry.load_adapters()
    
    # Run once to warm cache
    print("--- RUNNING GREENHOUSE (DATABRICKS) - WARMING CACHE ---")
    run_benchmark("Databricks", "GREENHOUSE", "https://boards.greenhouse.io/databricks")
    
    # Run again to test cache hit
    print("--- RUNNING GREENHOUSE (DATABRICKS) - CACHE HIT ---")
    run_benchmark("Databricks", "GREENHOUSE", "https://boards.greenhouse.io/databricks")
    
    run_benchmark("Airbnb", "GREENHOUSE", "https://boards.greenhouse.io/airbnb")
    
    run_benchmark("Spotify", "LEVER", "https://jobs.lever.co/spotify")
    run_benchmark("GoPuff", "LEVER", "https://jobs.lever.co/gopuff")
    
    run_benchmark("Microsoft", "PHENOM", "https://careers.microsoft.com/v2/global/en/home.html")
    
    # We will use an example Workday URL since specific ones aren't listed
    run_benchmark("Mastercard", "WORKDAY", "https://mastercard.wd1.myworkdayjobs.com/CorporateCareers")
    
    run_benchmark("Wipro", "SUCCESSFACTORS_RMK", "https://careers.wipro.com/careers-home")
