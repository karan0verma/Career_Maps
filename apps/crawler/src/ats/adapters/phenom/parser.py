from typing import List, Dict, Any
from src.dto.job_normalized_dto import JobNormalizedDTO

def parse_job(raw_job: Dict[str, Any], company_name: str, pcs_domain: str) -> JobNormalizedDTO:
    """Parses a Phenom People (or PCSX) job dictionary into a JobNormalizedDTO."""
    # externalJobId
    external_job_id = str(raw_job.get("displayJobId") or raw_job.get("atsJobId") or raw_job.get("id", ""))
    
    # Title
    title = raw_job.get("name", "Unknown Title")
    
    # Category / Department
    category = raw_job.get("department", "General")
    
    # Location handling (locations is usually a list)
    location_str = None
    city = None
    state = None
    country = None
    
    locations = raw_job.get("locations", [])
    if not locations and "location" in raw_job:
        # Sometimes location is a string or dict
        if isinstance(raw_job["location"], str):
            locations = [raw_job["location"]]
            
    if locations:
        loc = locations[0]
        if isinstance(loc, str):
            location_str = loc
            parts = [p.strip() for p in loc.split(",")]
            if len(parts) >= 3:
                # E.g., "Australia, New South Wales, Sydney"
                # Some are "United States, Washington, Redmond"
                country = parts[0]
                state = parts[1]
                city = parts[2]
            elif len(parts) == 2:
                # E.g., "Bangalore, India"
                city = parts[0]
                country = parts[1]
            else:
                city = parts[0]
                
    # Employment Type (often embedded in tags or standard field, default to Full-time)
    employment_type = "Full-time"
    
    # Apply URL
    position_url = raw_job.get("positionUrl", "")
    if position_url and not position_url.startswith("http"):
        # e.g., "/careers/job/1970393556912947"
        apply_url = f"https://{pcs_domain}{position_url}"
    else:
        apply_url = position_url or f"https://{pcs_domain}/"
        
    return {
        "externalJobId": external_job_id,
        "title": title,
        "description": None,
        "location": location_str,
        "city": city,
        "state": state,
        "country": country,
        "employmentType": employment_type,
        "experience": None,
        "applyUrl": apply_url,
        "sourceATS": "PHENOM",
        "department": category
    }
