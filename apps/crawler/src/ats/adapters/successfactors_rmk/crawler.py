import logging
import json
import re
from urllib.parse import urlparse
from typing import List, Optional, Dict, Any

from src.playwright_crawler import PlaywrightCrawler
from src.ats.registry import AtsRegistry
from src.dto.job_normalized_dto import JobNormalizedDTO
from src.dto.crawler_context import CrawlerContext
from .parser import parse_job_json, parse_job_html

logger = logging.getLogger(__name__)

class _RmkApiStrategy:
    """Strategy for CSB SPA sites that use /services/recruiting/v1/jobs."""
    def __init__(self, page, api_url: str, csrf_token: str, base_domain: str, referrer: str):
        self.page = page
        self.api_url = api_url
        self.csrf_token = csrf_token
        self.base_domain = base_domain
        self.referrer = referrer
        
    def execute(self, company_id: str, company_name: str) -> List[Dict[str, Any]]:
        logger.info("Executing RMK API Strategy...")
        jobs = []
        page_number = 0
        has_more = True
        
        while has_more:
            logger.info(f"Fetching API page {page_number}...")
            payload = {
                "locale": "en_US",
                "pageNumber": page_number,
                "sortBy": "",
                "keywords": "",
                "location": "",
                "facetFilters": {},
                "categoryId": 0
            }
            
            # Use Playwright's evaluate to make the fetch request to avoid CORS/Cookie issues
            try:
                response_json = self.page.evaluate('''async ([url, token, payload, referrer]) => {
                    let r = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'x-csrf-token': token,
                            'Referer': referrer
                        },
                        body: JSON.stringify(payload)
                    });
                    if (!r.ok) return null;
                    return await r.json();
                }''', [self.api_url, self.csrf_token, payload, self.referrer])
            except Exception as e:
                logger.warning(f"Fetch failed: {e}")
                response_json = None
            
            if not response_json:
                logger.warning("Empty response from API.")
                break
                
            page_jobs = parse_job_json(response_json, company_id, company_name, self.base_domain)
            if not page_jobs:
                break
                
            jobs.extend(page_jobs)
            logger.info(f"Parsed {len(page_jobs)} jobs on API page {page_number}")
            
            # Pagination Logic: Unfortunately the API doesn't always return totalPages clearly, 
            # or it might. Let's just check if we got jobs. If less than typical page size (often 10 or 25), stop.
            if len(page_jobs) < 5: # Assuming RMK returns at least > 5 if there's a next page, or we just stop when 0.
                has_more = False
                
            # If we get zero jobs, we definitely stop
            if len(page_jobs) == 0:
                has_more = False
                
            # Hard limit to prevent infinite loops
            if page_number >= 20: 
                logger.warning("Reached maximum API pages (20). Stopping.")
                break
                
            page_number += 1
            
        return jobs

class _RmkHtmlStrategy:
    """Strategy for Legacy/SSR sites that use /search/?startrow=X."""
    def __init__(self, page, search_base_url: str, base_domain: str):
        self.page = page
        self.search_base_url = search_base_url
        self.base_domain = base_domain
        
    def execute(self, company_id: str, company_name: str) -> List[Dict[str, Any]]:
        logger.info("Executing RMK HTML Strategy...")
        jobs = []
        startrow = 0
        has_more = True
        
        while has_more:
            url = f"{self.search_base_url}?startrow={startrow}&format=json" # format=json is a standard RMK hack to get cleaner HTML sometimes
            logger.info(f"Navigating to HTML page startrow={startrow}: {url}")
            
            self.page.goto(url, wait_until="networkidle")
            
            # Give it a second to render
            self.page.wait_for_timeout(1000)
            
            html = self.page.content()
            
            page_jobs = parse_job_html(html, company_id, company_name, self.base_domain)
            if not page_jobs:
                logger.info("No jobs found on this page. Ending pagination.")
                break
                
            jobs.extend(page_jobs)
            logger.info(f"Parsed {len(page_jobs)} jobs from HTML starting at row {startrow}")
            
            # Standard RMK pagination step is usually 25, 50, or whatever. We can just step by the number of jobs found!
            # If we found less than 10, it's probably the last page.
            if len(page_jobs) == 0:
                has_more = False
                
            # Usually step by 25
            startrow += 25
            
            if startrow > 1000: # Safe limit
                break
                
        return jobs

@AtsRegistry.register("SUCCESSFACTORS_RMK")
class SuccessFactorsRmkCrawler(PlaywrightCrawler):
    
    def __init__(self, company):
        super().__init__(company)
        self.strategy = None
        
    def login(self, context: CrawlerContext):
        """
        Determines the internal strategy (API vs HTML) by analyzing the page.
        """
        parsed_url = urlparse(self.career_url)
        base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        logger.info(f"Testing RMK pattern for {base_domain}...")
        
        # RMK search URLs are usually under /search/ or root
        search_path = "/search/" if not self.career_url.endswith("/search/") else ""
        search_url = self.career_url.rstrip("/") + search_path
        
        context.page.goto(search_url, wait_until="networkidle")
        context.page.wait_for_timeout(2000) # Give scripts time to execute
        
        html = context.page.content()
        
        # 1. Attempt to find CSRF token for Pattern B
        csrf_token = None
        match = re.search(r'CSRFToken\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE)
        if match:
            csrf_token = match.group(1)
            
        if not csrf_token:
            # Another common pattern is inside meta tags or X-CSRF-Token configurations
            match = re.search(r'["\']X-CSRF-Token["\']\s*:\s*["\']([^"\']+)["\']', html, re.IGNORECASE)
            if match:
                csrf_token = match.group(1)
                
        api_url = f"{base_domain}/services/recruiting/v1/jobs"
        
        if csrf_token:
            logger.info(f"Found CSRF Token: {csrf_token[:10]}... Testing API.")
            
            # Test if the API actually works (some legacy sites have CSRF but API is disabled)
            payload = {"locale": "en_US", "pageNumber": 0}
            api_ok = False
            try:
                api_ok = context.page.evaluate('''async ([url, token, payload, referrer]) => {
                    let r = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'x-csrf-token': token,
                            'Referer': referrer
                        },
                        body: JSON.stringify(payload)
                    });
                    return r.status === 200;
                }''', [api_url, csrf_token, payload, search_url])
            except Exception as e:
                logger.warning(f"API test failed: {e}")
                
            if api_ok:
                logger.info("API is responding (200 OK). Pattern B (API) identified.")
                self.strategy = _RmkApiStrategy(
                    page=context.page, 
                    api_url=api_url, 
                    csrf_token=csrf_token, 
                    base_domain=base_domain,
                    referrer=search_url
                )
            else:
                logger.info("API returned error (e.g. 405). Falling back to Pattern A (HTML).")
                self.strategy = _RmkHtmlStrategy(
                    page=context.page,
                    search_base_url=search_url,
                    base_domain=base_domain
                )
        else:
            logger.info("No CSRF Token found. Pattern A (HTML) identified.")
            self.strategy = _RmkHtmlStrategy(
                page=context.page,
                search_base_url=search_url,
                base_domain=base_domain
            )
            
        return True
        
    def crawl(self, context: CrawlerContext) -> List[Dict[str, Any]]:
        if not self.strategy:
            logger.error("Crawler strategy was not initialized in login().")
            return []
            
        return self.strategy.execute(self.company_id, self.company_name)
        
    def parse(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Parsing is handled inside the strategies, which return List[Dict[str, Any]]
        return raw_data
        
    def normalize(self, parsed_data: List[Dict[str, Any]]) -> List[JobNormalizedDTO]:
        normalized_jobs = []
        for data in parsed_data:
            dto = JobNormalizedDTO(
                companyId="",
                companyName=self.company_name,
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
                sourceATS=data.get("sourceATS", "SUCCESSFACTORS_RMK"),
                department=data.get("department")
            )
            normalized_jobs.append(dto)
        return normalized_jobs
