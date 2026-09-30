from playwright.sync_api import sync_playwright
from src.crawlers.swiggy_crawler import SwiggyCrawler

def test_swiggy():
    crawler = SwiggyCrawler(
        company_id="swiggy-test",
        company_name="Swiggy",
        career_url="https://careers.swiggy.com/"
    )
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print("Logging in...")
            crawler.login(page)
            
            print("Crawling...")
            raw_jobs = crawler.crawl(page)
            
            print(f"Found {len(raw_jobs)} raw jobs")
            if raw_jobs:
                print("Parsing...")
                parsed_jobs = crawler.parse(raw_jobs)
                
                print("Normalizing...")
                normalized_jobs = crawler.normalize(parsed_jobs)
                
                for job in normalized_jobs:
                    print(job)
            else:
                print("No jobs found, likely blocked by anti-bot.")
        except Exception as e:
            print(f"Error during test: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    test_swiggy()
