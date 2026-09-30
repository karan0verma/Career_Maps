from src.ats.registry import AtsRegistry
from src.ats.adapters.lever.crawler import LeverCrawler
import time
import json

def test_company(name, url):
    print(f"\n==============================================")
    print(f"Testing {name} via LeverCrawler")
    print(f"==============================================")
    
    config = {
        "id": f"test-{name.lower()}",
        "companyName": name,
        "officialCareerPage": url,
        "opportunities": []
    }
    
    start = time.time()
    crawler = LeverCrawler(config)
    result = crawler.execute()
    end = time.time()
    
    print("\n--- RESULTS ---")
    print(f"Status: {result.get('status')}")
    print(f"Total Live Jobs: {result.get('totalLiveJobs')}")
    print(f"Execution Time: {end - start:.2f}s")
    
    if result.get("totalLiveJobs", 0) > 0:
        sample = result.get("newOpportunities", [])[0]
        print(f"Sample Job Output:\n{json.dumps(sample, indent=2)}")

def main():
    # Force import of all adapters so they register
    AtsRegistry.load_adapters()
    print("Available adapters:", AtsRegistry._registry.keys())
    
    test_company("Spotify", "https://jobs.lever.co/spotify")
    test_company("Palantir", "https://jobs.lever.co/palantir")
    test_company("GoPuff", "https://jobs.lever.co/gopuff")
    test_company("Wealthfront", "https://jobs.lever.co/wealthfront")

if __name__ == "__main__":
    main()
