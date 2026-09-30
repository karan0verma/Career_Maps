import asyncio
import logging
from src.ats.adapters.greenhouse.crawler import GreenhouseCrawler

logging.basicConfig(level=logging.INFO)

def run_test(company_name: str, career_url: str):
    print(f"\n{'='*50}\nTesting {company_name}\n{'='*50}")
    
    company_data = {
        "id": f"test-{company_name.lower()}",
        "companyName": company_name,
        "officialCareerPage": career_url,
        "opportunities": []
    }
    
    crawler = GreenhouseCrawler(company_data)
    result = crawler.execute()
    
    new_opps = result.get("newOpportunities", [])
    print(f"Crawled {len(new_opps)} jobs!")
    if new_opps:
        sample = new_opps[0]
        print(f"Sample job 1: {sample['title']} | {sample['location']} | {sample['applyUrl']} | {sample['externalJobId']}")
        print(f"Sample job 2: {new_opps[1]['title']} | {new_opps[1]['location']} | {new_opps[1]['applyUrl']} | {new_opps[1]['externalJobId']}")

def main():
    test_cases = [
        ("Airbnb", "https://careers.airbnb.com"),
        ("Stripe", "https://stripe.com/jobs"),
        ("Figma", "https://www.figma.com/careers/"),
        ("Databricks", "https://databricks.com/company/careers/open-positions"),
    ]
    
    for name, url in test_cases:
        run_test(name, url)

if __name__ == "__main__":
    main()
