import logging
from typing import Dict, Any, List
from src.http_crawler import HttpCrawler
from src.ats.registry import AtsRegistry
from src.dto.crawler_context import CrawlerContext
from src.services.html_parser.service import HtmlParserService

logger = logging.getLogger(__name__)

@AtsRegistry.register("BAMBOOHR")
class BambooHRCrawler(HttpCrawler):
    """
    BambooHR Crawler using embedded HTML JSON extraction.
    URL Format: https://{token}.bamboohr.com/careers
    """
    def __init__(self, target_config: Dict[str, Any]):
        super().__init__(target_config)
        self.ats_type = "BAMBOOHR"
        self.token = target_config.get("token")

    def login(self, context: CrawlerContext) -> None:
        from src.services.token_discovery.service import TokenDiscoveryService
        if not self.token:
            self.token = TokenDiscoveryService.resolve_token(
                ats_type="BAMBOOHR",
                company_url=self.career_url,
                company_name=self.company_name
            )

    def crawl(self, context: CrawlerContext) -> Any:
        token = self.token
        if not token:
            logger.error(f"[{self.company_name}] Token missing for BambooHR")
            return None
            
        url = f"https://{token}.bamboohr.com/careers"
        logger.info(f"[{self.company_name}] Fetching BambooHR HTML: {url}")
        
        # 1. Fetch raw HTML
        html_content = self._fetch_html(url, context)
        if not html_content:
            return None
            
        # 2. Extract embedded JSON using shared HtmlParserService
        # BambooHR typically embeds jobs in window.BambooHR or INITIAL_STATE
        json_data = HtmlParserService.extract_json_from_script(html_content, r'window\.BambooHR\s*=\s*(\{.*?\});')
        
        if not json_data:
            json_data = HtmlParserService.extract_json_from_script(html_content, r'INITIAL_STATE\s*=\s*(\{.*?\});')
            
        if not json_data:
            # Maybe the raw list API works for this company?
            api_url = f"https://{token}.bamboohr.com/careers/list"
            logger.info(f"[{self.company_name}] Embedded JSON not found, trying fallback API: {api_url}")
            fallback_data = self._fetch_json(api_url, context)
            if fallback_data and isinstance(fallback_data, dict):
                return fallback_data
            
        return json_data

    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        from .parser import BambooHRParser
        if not raw_data:
            return []
        return BambooHRParser.parse_jobs(raw_data)
