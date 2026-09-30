from src.crawlers.workday_crawler import WorkdayCrawler
import json

company = {
    "id": "test-workday-mastercard",
    "companyName": "Mastercard",
    "slug": "mastercard",
    "officialCareerPage": "https://mastercard.wd1.myworkdayjobs.com/CorporateCareers",
    "opportunities": []
}

crawler = WorkdayCrawler(company)
jobs = crawler.crawl(None)
parsed = crawler.parse(jobs)
normalized = crawler.normalize(parsed)

print(f"Total normalized jobs: {len(normalized)}")
if normalized:
    print("Sample job:")
    print(json.dumps(normalized[0], indent=2))
