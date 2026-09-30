from src.ats.registry import AtsRegistry
from src.ats.adapters.greenhouse.crawler import GreenhouseCrawler
import time

def main():
    print("Available adapters:", AtsRegistry._registry.keys())
    
    databricks_config = {
        "id": "test-databricks",
        "companyName": "Databricks",
        "officialCareerPage": "https://www.databricks.com/company/careers/open-positions",
        "opportunities": []
    }
    
    print("\nInitializing GreenhouseCrawler for Databricks...")
    start_time = time.time()
    crawler = GreenhouseCrawler(databricks_config)
    result = crawler.execute()
    end_time = time.time()
    
    print("\n--- RESULTS ---")
    print(f"Status: {result.get('status')}")
    print(f"Total Live Jobs: {result.get('totalLiveJobs')}")
    print(f"Total Execution Time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
