from playwright.sync_api import sync_playwright
import sys
import os

# Ensure src module is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.crawlers.microsoft_crawler import MicrosoftCrawler

def test_microsoft_crawler():
    crawler = MicrosoftCrawler()
    crawler.company_id = "microsoft"
    crawler.company_name = "Microsoft"
    crawler.career_url = "https://jobs.careers.microsoft.com/global/en/search"
    
    print("Starting Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Logging in (navigating to jobs page)...")
        crawler.login(page)
        
        print("Crawling...")
        raw_elements = crawler.crawl(page)
        
        if not raw_elements:
            print("No elements found or blocked by anti-bot.")
            browser.close()
            return
            
        print("Parsing...")
        parsed_data = crawler.parse(raw_elements)
        print(f"Parsed {len(parsed_data)} items. First 3: {parsed_data[:3]}")
        
        print("Normalizing...")
        normalized = crawler.normalize(parsed_data)
        print(f"Normalized {len(normalized)} items. First 3: {normalized[:3]}")
        
        browser.close()

if __name__ == "__main__":
    test_microsoft_crawler()
