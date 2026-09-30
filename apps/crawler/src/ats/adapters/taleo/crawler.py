import re
from typing import Any, List, Dict
from bs4 import BeautifulSoup
from src.playwright_crawler import PlaywrightCrawler
from src.ats.registry import AtsRegistry
from src.dto.job_normalized_dto import JobNormalizedDTO
from src.dto.crawler_context import CrawlerContext

@AtsRegistry.register("TALEO")
class TaleoCrawler(PlaywrightCrawler):
    """
    Taleo Adapter.
    Extracts jobs from Taleo Enterprise and Taleo Business Edition.
    """
    def __init__(self, company_data: Dict[str, Any]):
        super().__init__(company_data)
        
    def login(self, context: CrawlerContext) -> None:
        pass
        
    def crawl(self, context: CrawlerContext) -> Any:
        print(f"[{self.company_name}] Fetching jobs from Taleo...")
        page = context.page
        
        try:
            page.goto(self.career_url, wait_until='networkidle', timeout=30000)
            
            # Simple heuristic: scroll down to load jobs if it's dynamic
            for _ in range(3):
                page.evaluate("window.scrollBy(0, 1000)")
                page.wait_for_timeout(1000)
                
            html = page.content()
            return html
            
        except Exception as e:
            print(f"[{self.company_name}] Taleo crawl failed: {e}")
            return ""

    def parse(self, raw_data: Any) -> list:
        if not raw_data:
            return []
            
        soup = BeautifulSoup(raw_data, 'html.parser')
        parsed = []
        
        # Taleo often uses table rows for jobs, or specific div classes
        # This is a generalized selector targeting common Taleo elements
        job_elements = soup.find_all('div', class_=re.compile(r'job.*|requisition.*', re.I))
        if not job_elements:
            job_elements = soup.find_all('tr', class_=re.compile(r'listitem.*', re.I))
            
        for el in job_elements:
            title_el = el.find(['h2', 'h3', 'a'], class_=re.compile(r'.*title.*', re.I))
            if not title_el:
                title_el = el.find('a', href=re.compile(r'.*job.*|.*req.*', re.I))
                
            if not title_el:
                continue
                
            title = title_el.get_text(strip=True)
            href = title_el.get('href')
            
            apply_url = ""
            if href:
                if href.startswith('http'):
                    apply_url = href
                else:
                    apply_url = self.career_url.rstrip('/') + '/' + href.lstrip('/')
                    
            location_el = el.find(['span', 'div'], class_=re.compile(r'.*location.*', re.I))
            location = location_el.get_text(strip=True) if location_el else ""
            
            job_id_el = el.find(string=re.compile(r'Req ID.*|Job Number.*', re.I))
            external_job_id = None
            if job_id_el:
                m = re.search(r'(?:Req ID|Job Number)[:\-]?\s*([A-Za-z0-9_-]+)', str(job_id_el), re.I)
                if m:
                    external_job_id = m.group(1)
            
            if not external_job_id:
                # Try to get from url
                m = re.search(r'job=([A-Za-z0-9_-]+)|req=([A-Za-z0-9_-]+)', apply_url, re.I)
                if m:
                    external_job_id = m.group(1) or m.group(2)
                else:
                    external_job_id = apply_url.split('/')[-1] if apply_url else title
            
            parsed.append({
                "title": title,
                "location": location,
                "apply_url": apply_url,
                "external_job_id": external_job_id
            })
            
        return parsed

    def normalize(self, parsed_data: list) -> List[JobNormalizedDTO]:
        normalized = []
        for job in parsed_data:
            if not job.get("title") or not job.get("external_job_id"): continue
            
            dto = JobNormalizedDTO(
                companyId=self.company_id,
                companyName=self.company_name,
                externalJobId=job["external_job_id"],
                title=job["title"],
                description=None,
                location=job.get("location"),
                city=None,
                state=None,
                country=None,
                employmentType=None,
                experience=None,
                applyUrl=job["apply_url"],
                sourceATS="TALEO"
            )
            normalized.append(dto)
        return normalized
