from typing import List, Dict, Any

def parse_eightfold_jobs(jobs: List[Dict[str, Any]], company_id: str, company_name: str, source_ats: str) -> List[Dict[str, Any]]:
    parsed_jobs = []
    
    for job in jobs:
        # Eightfold uses 'id' as the unique identifier
        job_id = job.get('id')
        if not job_id:
            continue
            
        title = job.get('name', '')
        description = job.get('jobDescription', '')
        department = job.get('department', '')
        
        locations = job.get('locations', [])
        location = locations[0] if locations else job.get('location', '')
        
        # Determine workplace type
        workplace_type = "On-site"
        if location and ("remote" in location.lower() or "anywhere" in location.lower()):
            workplace_type = "Remote"
            
        apply_url = job.get('url') or job.get('applyUrl', '')
        
        parsed_job = {
            "externalJobId": str(job_id),
            "title": title,
            "description": description,
            "location": location,
            "department": department,
            "workplaceType": workplace_type,
            "applyUrl": apply_url,
            "sourceATS": source_ats
        }
        
        parsed_jobs.append(parsed_job)
        
    return parsed_jobs
