import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import sync_playwright
from src.crawlers.tcs_crawler import TCSCrawler

def test_tcs_crawler():
    crawler = TCSCrawler(company_id="tcs", company_name="TCS", career_url="https://www.tcs.com/careers")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Logging in to TCS careers...")
        crawler.login(page)
        
        print("Crawling...")
        raw_data = crawler.crawl(page)
        
        print("Parsing...")
        parsed_data = crawler.parse(raw_data)
        
        print("Normalizing...")
        normalized_data = crawler.normalize(parsed_data)
        
        print(f"Found {len(normalized_data)} jobs.")
        for job in normalized_data[:5]:
            print(job)
            
        browser.close()

if __name__ == "__main__":
    test_tcs_crawler()
