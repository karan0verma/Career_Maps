from typing import Any, List, Dict
from playwright.sync_api import Page
from src.base_crawler import BaseCrawler
from src.ats.registry import AtsRegistry
from src.dto.job_normalized_dto import JobNormalizedDTO

@AtsRegistry.register("UNKNOWN")
class UnknownCrawler(BaseCrawler):
    """
    Fallback crawler when the ATS is proprietary or custom.
    Presently, the user has restricted building company-specific crawlers.
    This acts as a stub to prevent crashes.
    """
    
    def __init__(self, company_data: Dict[str, Any]):
        super().__init__(company_data)
        
    def login(self, page: Page) -> None:
        pass

    def crawl(self, page: Page) -> Any:
        print(f"[{self.company_name}] ATS is UNKNOWN. Custom adapter not implemented yet.")
        return []

    def parse(self, raw_data: Any) -> list:
        return []

    def normalize(self, parsed_data: list) -> List[JobNormalizedDTO]:
        return []
