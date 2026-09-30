import logging
from typing import Any, Dict
from src.http_crawler import HttpCrawler
from src.ats.registry import AtsRegistry
from src.dto.crawler_context import CrawlerContext
from src.ats.adapters.zohorecruit.parser import parse_zoho_jobs
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

@AtsRegistry.register("ZOHO_RECRUIT")
class ZohoRecruitCrawler(HttpCrawler):
    def __init__(self, target_config: Dict[str, Any]):
        super().__init__(target_config)
        self.ats_type = "ZOHO_RECRUIT"

    def crawl(self, context: CrawlerContext) -> Any:
        parsed_url = urlparse(self.career_url)
        base_url = f"https://{parsed_url.netloc}"
        
        # Standard public JSON endpoint for Zoho Recruit
        api_url = f"{base_url}/recruit/v2/public/Job_Openings"
        
        all_jobs = []
        page = 1
        limit = 100
        
        while True:
            params = {
                "page": page,
                "limit": limit
            }
            logger.info(f"Fetching Zoho Recruit jobs page={page} limit={limit}")
            
            # Using our shared infrastructure
            data = self._fetch_json(api_url, context, params=params)
            
            if not data or not isinstance(data, dict):
                # 400 or 404 might mean the company disabled public API access
                logger.warning(f"[{self.company_name}] Could not fetch or parse JSON from Zoho API.")
                break
                
            # Zoho data usually lives in 'data' array
            jobs = data.get("data", [])
            if not jobs:
                break
                
            all_jobs.extend(jobs)
            
            # If we received less than the limit, we're done
            if len(jobs) < limit:
                break
                
            page += 1
            
        return all_jobs

    def parse(self, raw_data: Any) -> list:
        if not raw_data:
            return []
        return parse_zoho_jobs(raw_data, self.company_id, self.company_name, self.ats_type, self.career_url)

    def normalize(self, parsed_data: list) -> list:
        # BaseCrawler takes care of mapping dict to JobNormalizedDTO
        return super().normalize(parsed_data)
