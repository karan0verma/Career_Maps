import logging
import re
from typing import Dict, Any, List
from src.playwright_crawler import PlaywrightCrawler
from src.dto.crawler_context import CrawlerContext
from src.dto.job_normalized_dto import JobNormalizedDTO

logger = logging.getLogger(__name__)

class GenericDOMExtractor(PlaywrightCrawler):
    def __init__(self, company_data: Dict[str, Any]):
        super().__init__(company_data)
        self.page_timeout = 20000  # Strict timeout for generic DOM crawling
        
    def crawl(self, context: CrawlerContext) -> Any:
        page = context.page
        logger.info(f"[{self.company_name}] Crawling generic DOM at {self.career_url}")
        
        try:
            page.goto(self.career_url, wait_until="domcontentloaded", timeout=self.page_timeout)
            # Give SPA a moment to render
            page.wait_for_timeout(3000)
            
            # Retrieve all links and text to find job cards
            elements_data = page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a'));
                    return links.map(a => {
                        return {
                            text: a.innerText.trim(),
                            href: a.href,
                            id: a.id || '',
                            className: a.className || ''
                        };
                    });
                }
            """)
            
            return elements_data
            
        except Exception as e:
            logger.warning(f"[{self.company_name}] GenericDOMExtractor navigation failed: {e}")
            return []

    def parse(self, raw_data: Any) -> list:
        if not isinstance(raw_data, list):
            return []
            
        config = self.company.get("metadata", {}).get("extraction_config", {})
        if config and config.get("job_selector"):
            # If we have a declarative config, we don't use raw_data heuristics.
            # wait, `raw_data` here is the result of `page.evaluate`.
            # To do declarative parsing properly, `crawl` needs to return the elements based on `job_selector`.
            # Let's adjust this: if we want a robust dom extractor, we should just extract everything 
            # and let the script handle it, or we do evaluation in `crawl`.
            pass

        # For now, if config exists, we expect it to be parsed in `crawl` or we can just fall back to heuristic
        job_keywords = ['job', 'engineer', 'developer', 'analyst', 'manager', 'intern', 'consultant', 'designer', 'specialist', 'recruiter', 'associate', 'director', 'lead']
        
        jobs = []
        seen_urls = set()
        
        for item in raw_data:
            text = item.get('text', '')
            href = item.get('href', '')
            
            if not text or not href:
                continue
                
            if href in seen_urls:
                continue
                
            text_lower = text.lower()
            
            # Simple heuristic
            if len(text) > 5 and any(kw in text_lower for kw in job_keywords):
                if text_lower in ['find a job', 'search jobs', 'all jobs', 'jobs', 'careers', 'opportunities']:
                    continue
                    
                # allow mapped fields if they were extracted
                jobs.append({
                    "title": item.get('title') or text,
                    "location": item.get('location', ''),
                    "applyUrl": href
                })
                seen_urls.add(href)
                
            if len(jobs) >= 50:
                break
                
        return jobs

    def normalize(self, parsed_data: list) -> List[JobNormalizedDTO]:
        normalized = []
        for item in parsed_data:
            title = item.get('title', '')
            apply_url = item.get('applyUrl', '')
            
            dto = JobNormalizedDTO(
                companyId=self.company_id,
                companyName=self.company_name,
                externalJobId="",
                title=str(title),
                description="",
                location="",
                city=None,
                state=None,
                country=None,
                experience=None,
                employmentType=None,
                applyUrl=str(apply_url),
                sourceATS="GENERIC_DOM"
            )
            normalized.append(dto)
        return normalized
