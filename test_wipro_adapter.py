import sys
import os

# Add the apps/crawler directory to sys.path so we can import src
sys.path.append(os.path.join(os.path.dirname(__file__), "apps", "crawler"))

from src.registry import CrawlerRegistry
from src.crawlers.wipro_crawler import WiproCrawler

def test_wipro_adapter():
    company_data = {
        "id": "wipro_123",
        "companyName": "Wipro",
        "officialCareerPage": "https://careers.wipro.com/",
        "opportunities": []
    }
    
    # Initialize the crawler
    crawler = WiproCrawler(company_data)
    
    print("Executing Wipro crawler...")
    result = crawler.execute()
    
    print("\nResult Payload:")
    import json
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_wipro_adapter()
