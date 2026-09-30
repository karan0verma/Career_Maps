import logging
from typing import Any, List
from src.http_crawler import HttpCrawler
from src.ats.adapters.workable.parser import parse_workable_json
from src.ats.registry import AtsRegistry
from src.services.token_discovery.service import TokenDiscoveryService
from src.dto.crawler_context import CrawlerContext

logger = logging.getLogger(__name__)

@AtsRegistry.register("WORKABLE")
class WorkableCrawler(HttpCrawler):
    def __init__(self, company_data: dict):
        super().__init__(company_data)
        self.board_token = None

    def login(self, context: CrawlerContext) -> None:
        self.board_token = self.company.get('metadata', {}).get('board_token')
        if not self.board_token:
            self.board_token = TokenDiscoveryService.resolve_token(
            ats_type="WORKABLE",
            company_url=self.career_url,
            company_name=self.company_name
        )

    def crawl(self, context: CrawlerContext) -> Any:
        if not self.board_token:
            logger.error(f"[{self.company_name}] Cannot crawl Workable without board token.")
            return []

        all_jobs = []
        next_token = ""
        url = f"https://apply.workable.com/api/v3/accounts/{self.board_token}/jobs"

        logger.info(f"[{self.company_name}] Fetching Workable job catalog")
        
        while True:
            payload = {
                "token": next_token,
                "query": "",
                "location": [],
                "department": [],
                "worktype": [],
                "remote": []
            }
            
            response_data = self._fetch_json(url, context, json_payload=payload, method="POST")
            
            jobs = response_data.get("results", [])
            if not jobs:
                break
                
            all_jobs.extend(jobs)
            logger.info(f"[{self.company_name}] Fetched {len(jobs)} jobs (next_token: {next_token})")
            
            next_token = response_data.get("nextPage")
            if not next_token:
                break
                
        return all_jobs

    def parse(self, raw_data: Any) -> list:
        if not raw_data:
            return []
        return parse_workable_json(raw_data, self.company_id, self.board_token)
