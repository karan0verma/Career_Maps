from typing import Dict, Any, List
import logging
from src.http_crawler import HttpCrawler
from src.ats.registry import AtsRegistry
from src.dto.crawler_context import CrawlerContext

logger = logging.getLogger(__name__)

@AtsRegistry.register("JOBVITE")
class JobviteCrawler(HttpCrawler):
    """
    Jobvite Crawler using XML feed API.
    URL Format: https://app.jobvite.com/CompanyJobs/Xml.aspx?c={token}
    """
    def __init__(self, target_config: Dict[str, Any]):
        super().__init__(target_config)
        self.ats_type = "JOBVITE"
        self.token = target_config.get("token")

    def login(self, context: CrawlerContext) -> None:
        from src.services.token_discovery.service import TokenDiscoveryService
        if not self.token:
            self.token = TokenDiscoveryService.resolve_token(
                ats_type="JOBVITE",
                company_url=self.career_url,
                company_name=self.company_name
            )

    def crawl(self, context: CrawlerContext) -> Any:
        # Jobvite XML requires a company hash token e.g., 'qyV9VfwP'
        token = self.token
        if not token:
            logger.error(f"[{self.company_name}] Token missing for Jobvite")
            return None
            
        url = f"https://app.jobvite.com/CompanyJobs/Xml.aspx?c={token}"
        logger.info(f"[{self.company_name}] Fetching Jobvite XML feed: {url}")
        
        # _fetch_xml handles backoff, session sharing, and safe ET parsing
        return self._fetch_xml(url, context)

    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        from .parser import JobviteParser
        if not raw_data:
            return []
        return JobviteParser.parse_jobs(raw_data)
