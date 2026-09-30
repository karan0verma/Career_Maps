from playwright.sync_api import sync_playwright
from src.ats.adapters.successfactors_rmk.crawler import SuccessFactorsRmkCrawler
import logging

logging.basicConfig(level=logging.INFO)

def test_crawler(company, name_desc):
    print(f"\n{'='*50}\nTesting {name_desc}\n{'='*50}")
    crawler = SuccessFactorsRmkCrawler(company)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Test login (initializes strategy)
        success = crawler.login(page)
        if not success:
            print("Login/Strategy selection failed!")
            browser.close()
            return
            
        print(f"Selected strategy: {type(crawler.strategy).__name__}")
        
        # Test crawl (executes strategy)
        jobs = crawler.crawl(page)
        
        print(f"Crawled {len(jobs)} jobs!")
        if jobs:
            print(f"Sample job 1: {jobs[0].title} | {jobs[0].location} | {jobs[0].applyUrl} | {jobs[0].externalJobId}")
            
        browser.close()

if __name__ == "__main__":
    wipro = {
        "id": "w1", 
        "companyName": "Wipro", 
        "officialCareerPage": "https://careers.wipro.com/search/",
        "atsType": "SUCCESSFACTORS_RMK"
    }
    benteler = {
        "id": "b1",
        "companyName": "Benteler",
        "officialCareerPage": "https://career.benteler.jobs/search/",
        "atsType": "SUCCESSFACTORS_RMK"
    }
    
    test_crawler(benteler, "Benteler (Expected: HTML Strategy)")
    test_crawler(wipro, "Wipro (Expected: API Strategy)")
