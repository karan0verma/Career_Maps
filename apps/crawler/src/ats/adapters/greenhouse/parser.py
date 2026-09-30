from typing import Dict, Any, List
from src.dto.job_normalized_dto import JobNormalizedDTO
import logging

logger = logging.getLogger(__name__)

def parse_job_json(data: Dict[str, Any], company_id: str, company_name: str) -> List[JobNormalizedDTO]:
    """
    Parser for Greenhouse Job Board API.
    Extracts jobs from the /v1/boards/{board_token}/jobs response.
    """
    jobs: List[JobNormalizedDTO] = []
    
    search_results = data.get("jobs", [])
    if not search_results:
        return jobs
        
    for item in search_results:
        title = item.get("title", "")
        url = item.get("absolute_url", "")
        external_id = str(item.get("id", ""))
        
        # Location mapping (Greenhouse provides a 'location' object with a 'name' field)
        location_obj = item.get("location", {})
        location = location_obj.get("name", "Unknown") if isinstance(location_obj, dict) else "Unknown"
        
        department = None
        if item.get("departments"):
            departments_list = [d.get("name") for d in item["departments"] if d.get("name")]
            if departments_list:
                department = " / ".join(departments_list)
        
        published_at = item.get("updated_at")
        
        if title and external_id and url:
            jobs.append(JobNormalizedDTO(
                companyId=company_id,
                companyName=company_name,
                title=title.strip(),
                location=location.strip() if location else "Unknown",
                applyUrl=url,
                externalJobId=external_id,
                sourceATS="GREENHOUSE",
                description="",
                city=None,
                state=None,
                country=None,
                employmentType=None,
                experience=None,
                department=department,
                publishedAt=published_at
            ))
        else:
            logger.warning(f"Failed to extract title, url, or id. title={title} url={url} id={external_id}")
            
    return jobs
