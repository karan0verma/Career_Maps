import sys
import os

# Add apps/crawler to sys.path so we can import src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright
from src.crawlers.meta_crawler import MetaCrawler

def main():
    crawler = MetaCrawler()
    crawler.company_id = "meta"
    crawler.company_name = "Meta"
    crawler.career_url = "https://www.metacareers.com/v2/jobs/?is_leadership=0&is_manager=0"

    print("Starting MetaCrawler test...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("1. Logging in (handling cookies)...")
        crawler.login(page)
        
        print("2. Crawling...")
        raw_data = crawler.crawl(page)
        
        print(f"3. Parsing {len(raw_data)} elements...")
        parsed_data = crawler.parse(raw_data)
        
        print("4. Normalizing...")
        normalized_data = crawler.normalize(parsed_data)
        
        print("\nResults:")
        if not normalized_data:
            print("No jobs found. (Possibly blocked by anti-bot)")
        else:
            for job in normalized_data[:5]:
                print(f"Title: {job['title']}, Location: {job['location']}, URL: {job['applyUrl']}")
                
        browser.close()

if __name__ == "__main__":
    main()
