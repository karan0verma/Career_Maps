from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from src.dto.job_normalized_dto import JobNormalizedDTO
import re
import logging

logger = logging.getLogger(__name__)

def parse_job_json(data: Dict[str, Any], company_id: str, company_name: str, base_domain: str = "") -> List[JobNormalizedDTO]:
    """
    Parser for SuccessFactors RMK CSB (Pattern B - JSON API).
    Extracts jobs from the /services/recruiting/v1/jobs response.
    """
    jobs = []
    
    # RMK puts results in a slightly nested structure
    search_results = data.get("jobSearchResult", [])
    if not search_results:
        return jobs
        
    for item in search_results:
        job_data = item.get("response", {})
        if not job_data:
            continue
            
        title = job_data.get("title") or job_data.get("unifiedStandardTitle", "")
        # Use seoUrl or construct the URL
        url = job_data.get("seoUrl", "")
        if not url:
            url_title = job_data.get("urlTitle", "")
            job_id = job_data.get("id", "")
            if url_title and job_id:
                url = f"{base_domain.rstrip('/')}/job/{url_title}/{job_id}/"
        
        # Location mapping (can be list or string)
        location = ""
        loc_short = job_data.get("jobLocationShort", [])
        if loc_short and isinstance(loc_short, list):
            location = loc_short[0]
        elif isinstance(loc_short, str):
            location = loc_short
            
        external_id = str(job_data.get("id", ""))
        
        if title and external_id:
            jobs.append({
                "companyName": company_name,
                "title": title,
                "location": location.strip() if location else "Unknown",
                "applyUrl": url,
                "externalJobId": external_id,
                "sourceATS": "SUCCESSFACTORS_RMK",
                "description": "",
                "city": None,
                "state": None,
                "country": None,
                "employmentType": None,
                "experience": None
            })
        else:
            logger.warning(f"Failed to extract title or id. title={title} id={external_id}")
            
    return jobs


def parse_job_html(html: str, company_id: str, company_name: str, base_domain: str) -> List[JobNormalizedDTO]:
    """
    Parser for SuccessFactors RMK Legacy/SSR (Pattern A - HTML).
    Extracts jobs from the <tr class="data-row"> elements.
    """
    jobs = []
    soup = BeautifulSoup(html, 'html.parser')
    
    rows = soup.select('tr.data-row')
    
    for row in rows:
        title_elem = row.select_one('.jobTitle a')
        if not title_elem:
            continue
            
        title = title_elem.get_text(strip=True)
        href = title_elem.get("href", "")
        
        if not href.startswith("http"):
            # Ensure it starts with /
            if not href.startswith("/"):
                href = "/" + href
            applyUrl = base_domain.rstrip("/") + href
        else:
            applyUrl = href
            
        # Extract ID from URL: e.g. /job/Spartanburg-Quality-Technician-II-SC-29301/1390067233/
        external_id = ""
        match = re.search(r'/(\d+)/?$', href)
        if match:
            external_id = match.group(1)
            
        location_elem = row.select_one('.jobLocation')
        location = location_elem.get_text(strip=True) if location_elem else "Unknown"
        
        if title and external_id:
            jobs.append({
                "companyName": company_name,
                "title": title,
                "location": location,
                "applyUrl": applyUrl,
                "externalJobId": external_id,
                "sourceATS": "SUCCESSFACTORS_RMK",
                "description": "",
                "city": None,
                "state": None,
                "country": None,
                "employmentType": None,
                "experience": None
            })
            
    return jobs
