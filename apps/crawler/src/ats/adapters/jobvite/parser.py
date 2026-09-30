from typing import Dict, Any, List
from src.services.xml_parser.service import XmlParserService
from datetime import datetime

class JobviteParser:
    @staticmethod
    def parse_jobs(xml_root) -> List[Dict[str, Any]]:
        jobs = XmlParserService.find_all_elements(xml_root, ".//job")
        raw_jobs = []
        for job_node in jobs:
            job_dict = XmlParserService.node_to_dict(job_node)
            
            # Map raw dictionary to our normalized schema expectations before BaseCrawler maps to DTO
            # Jobvite XML typically has <id>, <title>, <location>, <department>, <job-type>, <date>
            mapped = {
                "externalJobId": job_dict.get("id"),
                "title": job_dict.get("title"),
                "description": job_dict.get("description"),
                "location": job_dict.get("location"),
                "department": job_dict.get("department"),
                "team": job_dict.get("category"),  # Fallback for team
                "workplaceType": None, # Usually embedded in location or not present
                "publishedAt": job_dict.get("date"),
                "applyUrl": job_dict.get("apply-url") or job_dict.get("detail-url"),
                "jobUrl": job_dict.get("detail-url")
            }
            
            # Additional Jobvite specific cleanup
            if job_dict.get("jobtype"):
                mapped["employmentType"] = job_dict.get("jobtype")
                
            raw_jobs.append(mapped)
            
        return raw_jobs
