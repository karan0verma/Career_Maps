import logging
from typing import Any, List
from src.http_crawler import HttpCrawler
from src.ats.adapters.lever.parser import parse_job_json
from src.ats.registry import AtsRegistry
from src.services.token_discovery.service import TokenDiscoveryService
from src.dto.crawler_context import CrawlerContext

logger = logging.getLogger(__name__)

@AtsRegistry.register("LEVER")
class LeverCrawler(HttpCrawler):
    def __init__(self, company_data: dict):
        super().__init__(company_data)
        self.board_token = None

    def login(self, context: CrawlerContext) -> None:
        self.board_token = self.company.get('metadata', {}).get('board_token')
        if not self.board_token:
            self.board_token = TokenDiscoveryService.resolve_token(
            ats_type="LEVER",
            company_url=self.career_url,
            company_name=self.company_name
        )
        
    def crawl(self, context: CrawlerContext) -> Any:
        if not self.board_token:
            logger.error("Cannot crawl without Lever board token.")
            return []
            
        api_url = f"https://api.lever.co/v0/postings/{self.board_token}?mode=json"
        logger.info(f"Fetching job catalog from {api_url}")
        
        try:
            resp = context.session.get(api_url, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"API success. Returned {len(data)} raw jobs.")
                return data
            else:
                logger.error(f"API returned {resp.status_code}")
                return []
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return []
            
    def parse(self, raw_data: Any) -> list:
        if not raw_data:
            return []
        return parse_job_json(raw_data, self.company_id, self.company_name)
        
    def normalize(self, parsed_data: list) -> list:
        return parsed_data
