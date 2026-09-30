import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'crawler')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from src.ats.adapters.phenom.crawler import PhenomCrawler
from src.dto.crawler_context import CrawlerContext

def run_phenom():
    company = {
        "companyName": "Cognizant",
        "officialCareerPage": "https://careers.cognizant.com/india-en/jobs/",
        "atsType": "PHENOM"
    }
    crawler = PhenomCrawler(company)
    ctx = CrawlerContext()
    
    print("Executing Login to extract configuration...")
    crawler.login(ctx)
    print("PCS Domain:", crawler.pcs_domain)
    
    print("Executing Crawl...")
    jobs = crawler.crawl(ctx)
    print(f"Extracted {len(jobs)} jobs.")
    
    if jobs:
        print("Sample raw job:", jobs[0].keys() if isinstance(jobs[0], dict) else "Unknown")
        parsed = crawler.parse(jobs[0], ctx)
        norm = crawler.normalize(parsed, ctx)
        print("Normalized URL:", norm.applyUrl)

if __name__ == "__main__":
    run_phenom()
