import logging
from typing import Any, List
from src.http_crawler import HttpCrawler
from src.ats.adapters.ashby.parser import parse_ashby_graphql
from src.ats.registry import AtsRegistry
from src.services.token_discovery.service import TokenDiscoveryService
from src.dto.crawler_context import CrawlerContext

logger = logging.getLogger(__name__)

@AtsRegistry.register("ASHBY")
class AshbyCrawler(HttpCrawler):
    def __init__(self, company_data: dict):
        super().__init__(company_data)
        self.board_token = None

    def login(self, context: CrawlerContext) -> None:
        self.board_token = self.company.get('metadata', {}).get('board_token')
        if not self.board_token:
            self.board_token = TokenDiscoveryService.resolve_token(
            ats_type="ASHBY",
            company_url=self.career_url,
            company_name=self.company_name
        )

    def crawl(self, context: CrawlerContext) -> Any:
        if not self.board_token:
            logger.error(f"[{self.company_name}] Cannot crawl Ashby without board token.")
            return {}

        url = "https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams"
        payload = {
            "operationName": "ApiJobBoardWithTeams",
            "variables": {"organizationHostedJobsPageName": self.board_token},
            "query": "query ApiJobBoardWithTeams($organizationHostedJobsPageName: String!) { jobBoard: jobBoardWithTeams(organizationHostedJobsPageName: $organizationHostedJobsPageName) { teams { id name } jobPostings { id title locationName employmentType teamId } } }"
        }

        logger.info(f"[{self.company_name}] Fetching Ashby job catalog via GraphQL")
        response_data = self._fetch_json(url, context, json_payload=payload, method="POST")
        return response_data

    def parse(self, raw_data: Any) -> list:
        if not raw_data:
            return []
        return parse_ashby_graphql(raw_data, self.company_id, self.board_token)
