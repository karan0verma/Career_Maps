from src.ats.adapters.greenhouse.crawler import GreenhouseCrawler
from src.dto.crawler_context import CrawlerContext

config = {
    "companyName": "Cloudflare",
    "id": "cloudflare_com",
    "officialCareerPage": "https://www.cloudflare.com/careers/",
    "atsType": "GREENHOUSE"
}

crawler = GreenhouseCrawler(config)
res = crawler.execute()
print(f"Total Live Jobs: {res.get('totalLiveJobs')}")
print(f"New Opportunities: {len(res.get('newOpportunities', []))}")
