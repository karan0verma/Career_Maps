import re
from typing import Any, List, Dict
from bs4 import BeautifulSoup
from src.playwright_crawler import PlaywrightCrawler
from src.ats.registry import AtsRegistry
from src.dto.job_normalized_dto import JobNormalizedDTO
from src.dto.crawler_context import CrawlerContext

@AtsRegistry.register("ICIMS")
class ICIMSCrawler(PlaywrightCrawler):
    """
    iCIMS Adapter.
    Extracts jobs from standard iCIMS job portals (icims.com).
    """
    def __init__(self, company_data: Dict[str, Any]):
        super().__init__(company_data)
        
    def login(self, context: CrawlerContext) -> None:
        pass
        
    def crawl(self, context: CrawlerContext) -> Any:
        print(f"[{self.company_name}] Fetching jobs from iCIMS...")
        page = context.page
        
        try:
            # iCIMS often uses an iframe for the job list (icims_content_iframe)
            page.goto(self.career_url, wait_until='networkidle', timeout=30000)
            
            iframe = page.query_selector('iframe#icims_content_iframe')
            if iframe:
                frame = iframe.content_frame()
                if frame:
                    # Scroll within iframe
                    for _ in range(3):
                        frame.evaluate("window.scrollBy(0, 1000)")
                        page.wait_for_timeout(1000)
                    html = frame.content()
                else:
                    html = page.content()
            else:
                html = page.content()
                
            return html
            
        except Exception as e:
            print(f"[{self.company_name}] iCIMS crawl failed: {e}")
            return ""

    def parse(self, raw_data: Any) -> list:
        if not raw_data:
            return []
            
        soup = BeautifulSoup(raw_data, 'html.parser')
        parsed = []
        
        # iCIMS uses a specific layout, usually class "iCIMS_JobsTable" or similar
        job_rows = soup.find_all('div', class_=re.compile(r'.*job.*row.*', re.I))
        if not job_rows:
            job_rows = soup.find_all('a', class_=re.compile(r'.*job.*title.*', re.I))
            
        for row in job_rows:
            title_el = None
            if row.name == 'a':
                title_el = row
            else:
                title_el = row.find('a', class_=re.compile(r'.*title.*', re.I)) or row.find('a', href=re.compile(r'/jobs/'))
                
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
                    
            location_el = row.find('span', class_=re.compile(r'.*location.*', re.I))
            location = location_el.get_text(strip=True) if location_el else ""
            
            # iCIMS usually has a job id in the URL like /jobs/1234/job-title/job
            external_job_id = None
            if apply_url:
                m = re.search(r'/jobs/(\d+)/', apply_url, re.I)
                if m:
                    external_job_id = m.group(1)
            
            if not external_job_id:
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
                sourceATS="ICIMS"
            )
            normalized.append(dto)
        return normalized
