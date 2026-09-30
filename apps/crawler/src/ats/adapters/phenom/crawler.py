import requests
import re
import html
import urllib.parse
from typing import List, Any, Dict
from src.playwright_crawler import PlaywrightCrawler
from src.ats.registry import AtsRegistry
from src.ats.adapters.phenom.parser import parse_job
from src.dto.job_normalized_dto import JobNormalizedDTO
from src.dto.crawler_context import CrawlerContext

@AtsRegistry.register("PHENOM")
class PhenomCrawler(PlaywrightCrawler):
    
    def __init__(self, company_config: Any):
        super().__init__(company_config)
        self.pcs_domain = None
        self.base_domain = None
        
    def login(self, context: CrawlerContext) -> None:
        """Dynamically extract Phenom configuration from the official career page."""
        career_url = self.company.get('officialCareerPage')
        company_name = self.company.get('companyName')
        
        # Parse base domain for query param
        parsed_url = urllib.parse.urlparse(career_url)
        parts = parsed_url.netloc.split('.')
        self.base_domain = ".".join(parts[-2:])
        
        try:
            if context.page:
                # Use fully rendered page from Playwright to avoid redirect/SSR issues
                html_content = context.page.content()
            else:
                resp = requests.get(career_url, timeout=15)
                resp.raise_for_status()
                html_content = resp.text
            
            # Phenom/PCSX configs are often embedded in HTML encoded strings
            decoded_html = html.unescape(html_content)
            match = re.search(r'"pcsDomain"\s*:\s*"([^"]+)"', decoded_html)
            if match:
                self.pcs_domain = match.group(1)
            else:
                print(f"[{company_name}] Warning: Could not find pcsDomain in HTML. Falling back to apply.{parsed_url.netloc}")
                self.pcs_domain = f"apply.{parsed_url.netloc}"
                
        except Exception as e:
            print(f"[{company_name}] Error extracting Phenom config: {e}")
            self.pcs_domain = f"apply.{parsed_url.netloc}"

    def crawl(self, context: CrawlerContext) -> List[Dict[str, Any]]:
        raw_jobs = []
        company_name = self.company.get('companyName')
        if not self.pcs_domain:
            return raw_jobs
            
        start = 0
        limit = 50
        api_url = f"https://{self.pcs_domain}/api/pcsx/search"
        
        # Perform 1 request (limit=50) for this implementation, handling up to 50 jobs.
        # Can be expanded for advanced pagination later.
        params = {
            "domain": self.base_domain,
            "start": start,
            "limit": limit
        }
        
        try:
            print(f"[{company_name}] Fetching Phenom API: {api_url}")
            resp = requests.get(api_url, params=params, timeout=15)
            resp.raise_for_status()
            
            data = resp.json()
            if "data" in data and "positions" in data["data"]:
                jobs = data["data"]["positions"]
                raw_jobs.extend(jobs)
                print(f"[{company_name}] Successfully fetched {len(jobs)} jobs via Phenom API.")
            else:
                print(f"[{company_name}] Unexpected API response structure.")
                
        except Exception as e:
            print(f"[{company_name}] Phenom API request failed: {e}")
            
        return raw_jobs

    def parse(self, raw_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        parsed_jobs = []
        company_name = self.company.get('companyName')
        for raw in raw_jobs:
            try:
                data_dict = parse_job(raw, company_name, self.pcs_domain)
                parsed_jobs.append(data_dict)
            except Exception as e:
                print(f"[{company_name}] Error parsing job: {e}")
        return parsed_jobs

    def normalize(self, parsed_data: List[Dict[str, Any]]) -> List[JobNormalizedDTO]:
        company_name = self.company.get('companyName')
        normalized_jobs = []
        for data in parsed_data:
            dto = JobNormalizedDTO(
                companyId="",
                companyName=company_name,
                externalJobId=data.get("externalJobId", ""),
                title=data.get("title", ""),
                description=data.get("description"),
                location=data.get("location"),
                city=data.get("city"),
                state=data.get("state"),
                country=data.get("country"),
                employmentType=data.get("employmentType"),
                experience=data.get("experience"),
                applyUrl=data.get("applyUrl", ""),
                sourceATS=data.get("sourceATS", "PHENOM"),
                department=data.get("department")
            )
            normalized_jobs.append(dto)
        return normalized_jobs
