import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'crawler')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from src.ats.adapters.successfactors_rmk.crawler import SuccessFactorsRmkCrawler
from src.dto.crawler_context import CrawlerContext

def run_ey():
    company = {
        "companyName": "EY",
        "officialCareerPage": "https://careers.ey.com/ey/job/search",
        "atsType": "SUCCESSFACTORS_RMK"
    }
    crawler = SuccessFactorsRmkCrawler(company)
    ctx = CrawlerContext()
    
    print("Executing Login...")
    crawler.login(ctx)
    print("RMK Domain:", crawler.rmk_domain)
    
    print("Executing Crawl...")
    jobs = crawler.crawl(ctx)
    print(f"Extracted {len(jobs)} jobs.")
    
    if jobs:
        print("Parsing first 3 jobs...")
        for i in range(min(3, len(jobs))):
            parsed = crawler.parse(jobs[i], ctx)
            norm = crawler.normalize(parsed, ctx)
            print(f"Job {i+1}: {norm.title} | {norm.location} | {norm.applyUrl}")

if __name__ == "__main__":
    run_ey()
