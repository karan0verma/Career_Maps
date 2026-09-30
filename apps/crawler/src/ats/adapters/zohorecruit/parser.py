from typing import List, Dict, Any
from urllib.parse import urlparse

def parse_zoho_jobs(jobs: List[Dict[str, Any]], company_id: str, company_name: str, source_ats: str, career_url: str) -> List[Dict[str, Any]]:
    parsed_jobs = []
    
    parsed_url = urlparse(career_url)
    base_url = f"https://{parsed_url.netloc}"
    
    for job in jobs:
        # Zoho unique ID is usually 'id' or 'Job_Opening_ID'
        job_id = job.get('id') or job.get('Job_Opening_ID')
        if not job_id:
            continue
            
        title = job.get('Job_Title', '') or job.get('Title', '')
        description = job.get('Job_Description', '') or job.get('Description', '')
        department = job.get('Department', '')
        
        # Location fields in Zoho
        city = job.get('City', '')
        state = job.get('State', '')
        country = job.get('Country', '')
        
        location_parts = [p for p in [city, state, country] if p]
        location = ", ".join(location_parts) if location_parts else job.get('Location', '')
        
        # Calculate Job URL
        apply_url = job.get('Job_Opening_URL') or f"{base_url}/jobs/Careers/{job_id}"
        
        workplace_type = job.get('Remote_Job', 'No')
        is_remote = str(workplace_type).lower() in ['yes', 'true', '1']
        
        parsed_job = {
            "externalJobId": str(job_id),
            "title": title,
            "description": description,
            "location": location,
            "city": city,
            "state": state,
            "country": country,
            "department": department,
            "workplaceType": "Remote" if is_remote else "On-site",
            "applyUrl": apply_url,
            "sourceATS": source_ats
        }
        
        parsed_jobs.append(parsed_job)
        
    return parsed_jobs
