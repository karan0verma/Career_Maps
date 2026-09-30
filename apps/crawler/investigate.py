import os
import sys

# Ensure src is in the python path
sys.path.insert(0, os.path.abspath('.'))

from playwright.sync_api import sync_playwright
from src.registry import CrawlerRegistry
import src.crawlers.infosys_crawler  # ensure it is imported and registered

def test_crawler():
    CrawlerClass = CrawlerRegistry.get("infosys")
    if not CrawlerClass:
        print("Failed to find infosys crawler in registry.")
        return

    # Create dummy company info for initialization
    crawler = CrawlerClass(
        company_data={
            "id": "infosys_123",
            "companyName": "Infosys",
            "officialCareerPage": "https://www.infosys.com/careers.html",
            "opportunities": []
        }
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Testing login...")
        crawler.login(page)
        
        print("Testing crawl...")
        raw_data = crawler.crawl(page)
        
        print("Testing parse...")
        parsed_data = crawler.parse(raw_data)
        
        print("Testing normalize...")
        normalized = crawler.normalize(parsed_data)
        
        print("Crawler final output:", normalized)
        
        browser.close()

if __name__ == "__main__":
    test_crawler()
