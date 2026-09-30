import logging
from typing import Any, List
from src.http_crawler import HttpCrawler
from src.ats.adapters.smartrecruiters.parser import parse_smartrecruiters_json
from src.ats.registry import AtsRegistry
from src.services.token_discovery.service import TokenDiscoveryService
from src.dto.crawler_context import CrawlerContext

logger = logging.getLogger(__name__)

@AtsRegistry.register("SMARTRECRUITERS")
class SmartRecruitersCrawler(HttpCrawler):
    def __init__(self, company_data: dict):
        super().__init__(company_data)
        self.board_token = None

    def login(self, context: CrawlerContext) -> None:
        self.board_token = self.company.get('metadata', {}).get('board_token')
        if not self.board_token:
            self.board_token = TokenDiscoveryService.resolve_token(
            ats_type="SMARTRECRUITERS",
            company_url=self.career_url,
            company_name=self.company_name
        )

    def crawl(self, context: CrawlerContext) -> Any:
        if not self.board_token:
            logger.error(f"[{self.company_name}] Cannot crawl SmartRecruiters without board token.")
            return []

        all_jobs = []
        offset = 0
        limit = 100

        logger.info(f"[{self.company_name}] Fetching SmartRecruiters job catalog")
        
        while True:
            url = f"https://api.smartrecruiters.com/v1/companies/{self.board_token}/postings"
            params = {"limit": limit, "offset": offset}
            
            response_data = self._fetch_json(url, context, params=params)
            
            jobs = response_data.get("content", [])
            if not jobs:
                break
                
            all_jobs.extend(jobs)
            logger.info(f"[{self.company_name}] Fetched {len(jobs)} jobs (offset {offset})")
            
            if len(jobs) < limit:
                break
                
            offset += limit
            
        return all_jobs

    def parse(self, raw_data: Any) -> list:
        if not raw_data:
            return []
        return parse_smartrecruiters_json(raw_data, self.company_id)
