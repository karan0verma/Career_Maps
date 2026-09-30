import sys
import os
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'apps', 'crawler')))

from src.registry import CrawlerRegistry
import src.crawlers.amazon_crawler

def test():
    Crawler = CrawlerRegistry.get_crawler("amazon")
    crawler = Crawler(
        company_name="Amazon",
        company_id="amazon",
        career_url="https://amazon.jobs/en/search"
    )
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Logging in...")
        crawler.login(page)
        
        print("Crawling...")
        raw_data = crawler.crawl(page)
        print(f"Raw data length: {len(raw_data)}")
        
        print("Parsing...")
        parsed_data = crawler.parse(raw_data)
        
        print("Normalizing...")
        normalized = crawler.normalize(parsed_data)
        print(f"Normalized {len(normalized)} jobs.")
        for job in normalized[:2]:
            print(job)
            
        browser.close()

if __name__ == "__main__":
    test()
