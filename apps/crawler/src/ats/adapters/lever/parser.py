import datetime
import logging
from typing import Any, List, Dict
from src.dto.job_normalized_dto import JobNormalizedDTO

logger = logging.getLogger(__name__)

def parse_job_json(raw_jobs: List[Dict[str, Any]], company_id: str, company_name: str) -> List[JobNormalizedDTO]:
    parsed = []
    
    for job in raw_jobs:
        try:
            external_job_id = job.get("id")
            title = job.get("text")
            
            if not external_job_id or not title:
                continue
                
            categories = job.get("categories", {})
            location = categories.get("location")
            department = categories.get("department")
            team = categories.get("team")
            workplace_type = job.get("workplaceType")
            
            # Combine team and department if both exist
            full_dept = department
            if team and full_dept:
                full_dept = f"{department} - {team}"
            elif team:
                full_dept = team
                
            apply_url = job.get("applyUrl")
            job_url = job.get("hostedUrl") # Not directly in DTO but good for reference
            
            # Handle timestamps (milliseconds from epoch)
            created_at_ms = job.get("createdAt")
            published_at = None
            if created_at_ms:
                try:
                    published_at = datetime.datetime.fromtimestamp(created_at_ms / 1000.0).isoformat()
                except Exception:
                    pass
                    
            description = job.get("descriptionPlain")
            
            dto = JobNormalizedDTO(
                companyId=company_id,
                companyName=company_name,
                externalJobId=external_job_id,
                title=title,
                description=description,
                location=location,
                city=None,
                state=None,
                country=job.get("country"),
                employmentType=None,
                experience=None,
                applyUrl=apply_url or job_url,
                sourceATS="LEVER",
                department=department,
                team=team,
                workplaceType=workplace_type,
                publishedAt=published_at
            )
            
            parsed.append(dto)
        except Exception as e:
            logger.warning(f"Failed to parse Lever job: {e}")
            
    return parsed
