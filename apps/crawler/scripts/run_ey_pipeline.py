import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'crawler')))

import json
from playwright.sync_api import sync_playwright
from src.ats.adapters.successfactors_rmk.crawler import SuccessFactorsRmkCrawler
from src.dto.crawler_context import CrawlerContext

def run_ey():
    company = {
        "companyName": "EY",
        "officialCareerPage": "https://careers.ey.com/ey/job/search",
        "atsType": "SUCCESSFACTORS_RMK"
    }
    crawler = SuccessFactorsRmkCrawler(company)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = CrawlerContext()
        ctx.browser = browser
        ctx.page = browser.new_page()
        
        print("Executing Login to extract RMK config...")
        crawler.login(ctx)
        
        print("Executing Crawl...")
        jobs = crawler.crawl(ctx)
        print(f"Extracted {len(jobs)} jobs.")
        
        verified_jobs = []
        
        if jobs:
            print("Parsing and verifying jobs...")
            for i in range(len(jobs)):
                try:
                    parsed = crawler.parse(jobs[i], ctx)
                    norm = crawler.normalize(parsed, ctx)
                    
                    # Hard rule check
                    if "india" in (norm.location or "").lower() or "india" in (norm.country or "").lower():
                        verified_jobs.append({
                            "title": norm.title,
                            "location": norm.location,
                            "applyUrl": norm.applyUrl
                        })
                except Exception as e:
                    pass
        
        print(f"Filtered India jobs: {len(verified_jobs)}")
        with open("C:/Users/Ahana Singh/.gemini/antigravity/brain/b2157c5e-32e9-4e58-993a-3a6a43a0d53a/ey_jobs.json", "w") as f:
            json.dump(verified_jobs, f, indent=2)
            
        browser.close()

if __name__ == "__main__":
    run_ey()
