import logging
from typing import Any, Dict
from src.http_crawler import HttpCrawler
from src.ats.registry import AtsRegistry
from src.dto.crawler_context import CrawlerContext
from src.ats.adapters.eightfold.parser import parse_eightfold_jobs
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

@AtsRegistry.register("EIGHTFOLD")
class EightfoldCrawler(HttpCrawler):
    def __init__(self, target_config: Dict[str, Any]):
        super().__init__(target_config)
        self.ats_type = "EIGHTFOLD"
        self.domain_token = target_config.get("token")

    def login(self, context: CrawlerContext) -> None:
        from src.services.token_discovery.service import TokenDiscoveryService
        if not self.domain_token:
            self.domain_token = TokenDiscoveryService.resolve_token(
                ats_type="EIGHTFOLD",
                company_url=self.career_url,
                company_name=self.company_name
            )

    def crawl(self, context: CrawlerContext) -> Any:
        if not self.domain_token:
            logger.error(f"[{self.company_name}] Token missing for Eightfold")
            return []
            
        # Extract the base hostname to construct the API URL
        parsed_url = urlparse(self.career_url)
        base_url = f"https://{parsed_url.netloc}"
        api_url = f"{base_url}/api/apply/v2/jobs"
        
        all_jobs = []
        start = 0
        num = 50
        
        while True:
            params = {
                "domain": self.domain_token,
                "start": start,
                "num": num
            }
            logger.info(f"Fetching Eightfold jobs start={start} limit={num}")
            
            data = self._fetch_json(api_url, context, params=params)
            
            if not data or not isinstance(data, dict):
                break
                
            positions = data.get("positions", [])
            if not positions:
                break
                
            all_jobs.extend(positions)
            
            if len(positions) < num:
                break
                
            start += num
            
        return all_jobs

    def parse(self, raw_data: Any) -> list:
        if not raw_data:
            return []
        return parse_eightfold_jobs(raw_data, self.company_id, self.company_name, self.ats_type)

    def normalize(self, parsed_data: list) -> list:
        # BaseCrawler takes care of JobNormalizedDTO mapping
        return super().normalize(parsed_data)
