import re
import json
import requests
from typing import Any, List, Dict
from src.playwright_crawler import PlaywrightCrawler
from src.ats.registry import AtsRegistry
from src.dto.job_normalized_dto import JobNormalizedDTO
from src.dto.crawler_context import CrawlerContext

@AtsRegistry.register("WORKDAY")
class WorkdayCrawler(PlaywrightCrawler):
    """
    Universal Workday Adapter.
    Extracts tenant and site config from the officialCareerPage URL.
    Works for any company using myworkdayjobs.com.
    """
        
    def __init__(self, company_data: Dict[str, Any]):
        super().__init__(company_data)
        self.api_url = self._build_api_url(self.career_url)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        
    def _build_api_url(self, url: str) -> str:
        url = url.rstrip("/")
        
        # If the URL doesn't contain myworkdayjobs, it's likely an embedded iframe. Let's fetch it and extract the iframe src.
        if "myworkdayjobs.com" not in url:
            try:
                r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10, verify=False)
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(r.text, 'html.parser')
                iframe = soup.find('iframe')
                if iframe and iframe.get('src') and "myworkdayjobs.com" in iframe['src']:
                    url = iframe['src']
            except Exception:
                pass

        match = re.search(r"https://(.*?)\.(.*?)\.myworkdayjobs\.com/([^/]+)", url)
        if match:
            tenant = match.group(1)
            subdomain = match.group(2)
            site_id = match.group(3)
            return f"https://{tenant}.{subdomain}.myworkdayjobs.com/wday/cxs/{tenant}/{site_id}/jobs"
            
        # Fallback to direct probe based on company domain if URL is masked
        board_token = self.company.get("metadata", {}).get("board_token")
        if board_token and ":" in board_token:
            slug, node = board_token.split(":", 1)
            return f"https://{slug}.{node}.myworkdayjobs.com/wday/cxs/{slug}/{slug.capitalize()}/jobs"
            
        domain = self.company.get("domain", "")
        slug = domain.split(".")[0].lower() if domain else ""
        if not slug:
            return ""
            
        for node in ["wd1", "wd3", "wd5", "wd12"]:
            try:
                test_url = f"https://{slug}.{node}.myworkdayjobs.com/{slug.capitalize()}"
                r = requests.head(test_url, timeout=3, allow_redirects=True)
                if r.status_code == 200:
                    self.career_url = test_url
                    return f"https://{slug}.{node}.myworkdayjobs.com/wday/cxs/{slug}/{slug.capitalize()}/jobs"
            except Exception:
                pass
        return ""

    def login(self, context: CrawlerContext) -> None:
        pass

    def crawl(self, context: CrawlerContext) -> Any:
        if not self.api_url:
            print(f"[{self.company_name}] Failed to parse Workday URL config. URL: {self.career_url}")
            return []
            
        print(f"[{self.company_name}] Fetching jobs from Workday API: {self.api_url}")
        
        payload = {
            "limit": 20,
            "offset": 0
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            job_postings = data.get("jobPostings", [])
            print(f"[{self.company_name}] Successfully fetched {len(job_postings)} jobs via API.")
            return job_postings
            
        except Exception as e:
            print(f"[{self.company_name}] Workday API request failed: {e}")
            return []

    def parse(self, raw_data: Any) -> list:
        parsed = []
        for job in raw_data:
            title = job.get("title", "")
            location = job.get("locationsText", "")
            external_path = job.get("externalPath", "")
            
            # Use the bullet fields ID or external path ID as externalJobId
            # Usually ends in _R-xxxxx or similar
            external_job_id = None
            bullets = job.get("bulletFields", [])
            if bullets and len(bullets) > 0:
                external_job_id = bullets[0]
            if not external_job_id:
                # fallback
                external_job_id = external_path.split("_")[-1] if "_" in external_path else external_path
            
            base_domain = re.search(r"(https://.*?\.myworkdayjobs\.com/[^/]+)", self.api_url)
            apply_url = ""
            if base_domain and external_path:
                # Need to convert /wday/cxs/... back to standard board URL if possible
                board_match = re.search(r"(https://.*?\.myworkdayjobs\.com)/wday/cxs/[^/]+/([^/]+)", self.api_url)
                if board_match:
                    apply_url = f"{board_match.group(1)}/{board_match.group(2)}{external_path}"
                else:
                    apply_url = self.career_url
                
            parsed.append({
                "title": title,
                "location": location,
                "apply_url": apply_url,
                "external_job_id": external_job_id,
                "employmentType": job.get("timeType"),
                "publishedAt": job.get("postedOn")
            })
        return parsed

    def normalize(self, parsed_data: list) -> List[JobNormalizedDTO]:
        normalized = []
        for job in parsed_data:
            if not job.get("title") or not job.get("external_job_id"): continue
            
            location = job.get("location")
            city = None
            state = None
            country = None
            
            # Simple extraction for "City, State" or "City, Country"
            if location and "," in location:
                parts = [p.strip() for p in location.split(",")]
                if len(parts) >= 2:
                    city = parts[0]
                    # We don't guess if the second part is state or country. 
                    # If it's a known country format or state format, it would require a library.
                    # As requested, avoid guessing country=India or state=Unknown.
                    # We will store the full string in location, and city in city.
                    pass
            
            dto = JobNormalizedDTO(
                companyId=self.company_id,
                companyName=self.company_name,
                externalJobId=job["external_job_id"],
                title=job["title"],
                description=None,
                location=location,
                city=city,
                state=None,
                country=None,
                employmentType=job.get("employmentType"),
                experience=None,
                applyUrl=job["apply_url"],
                sourceATS="WORKDAY",
                publishedAt=job.get("publishedAt")
            )
            
            normalized.append(dto)
            
        return normalized
