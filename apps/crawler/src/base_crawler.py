import os
import time
import random
import traceback
from datetime import datetime
from typing import Dict, Any, List
from src.dto.job_normalized_dto import JobNormalizedDTO
from src.dto.crawler_context import CrawlerContext

class BaseCrawler:
    def __init__(self, company_data: Dict[str, Any]):
        self.company = company_data
        self.company_name = self.company.get("companyName")
        self.company_id = self.company.get("id")
        self.career_url = self.company.get("officialCareerPage")
        
        self.max_retries = 2
        
        self.start_time = None
        self.end_time = None
        self.status = "idle"
        self.error_message = None

    def random_delay(self):
        """Random delay of 2-5 seconds between requests."""
        time.sleep(random.uniform(2, 5))

    def execute(self) -> Dict[str, Any]:
        """
        Entrypoint for crawler execution. 
        Subclasses (PlaywrightCrawler, HttpCrawler) must override this to provide the execution 
        environment (context) and handle environment-specific retries and cleanup, 
        then call `_execute_lifecycle(context)`.
        """
        raise NotImplementedError("Subclasses must implement execute() to provide a CrawlerContext.")
        
    def _execute_lifecycle(self, context: CrawlerContext) -> Dict[str, Any]:
        """
        The core lifecycle common to all crawlers.
        Receives a configured CrawlerContext and executes the phases.
        """
        import requests
        import logging
        logger = logging.getLogger(__name__)

        attempt = 0
        raw_data = None

        while attempt <= self.max_retries:
            try:
                self.login(context)
                raw_data = self.crawl(context)
                break
            except requests.exceptions.HTTPError as e:
                status = e.response.status_code if e.response is not None else None
                if status in (429, 500, 502, 503, 504):
                    attempt += 1
                    if attempt > self.max_retries:
                        raise
                    logger.warning(f"[{self.company_name}] Transient HTTP error {status}, retrying... ({attempt}/{self.max_retries})")
                    self.random_delay()
                else:
                    raise  # Non-transient HTTP error (400, 401, 403, 404, etc.)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                attempt += 1
                if attempt > self.max_retries:
                    raise
                logger.warning(f"[{self.company_name}] Transient connection error: {e}, retrying... ({attempt}/{self.max_retries})")
                self.random_delay()
            except Exception as e:
                # Playwright TimeoutError can also be caught here, but for strict compliance we only retry specific ones
                if e.__class__.__name__ == 'TimeoutError':
                    attempt += 1
                    if attempt > self.max_retries:
                        raise
                    logger.warning(f"[{self.company_name}] Timeout error: {e}, retrying... ({attempt}/{self.max_retries})")
                    self.random_delay()
                else:
                    raise # JSON, XML, programming errors are not retried

        parsed_data = self.parse(raw_data)
        normalized_data = self.normalize(parsed_data)
        return normalized_data

    def _finalize_result(self, result_payload: Any) -> Any:
        """Simply returns the payload (List of DTOs). Execution status is handled by Dispatcher."""
        return result_payload if result_payload is not None else []

    def login(self, context: CrawlerContext) -> None:
        """
        Optional step to handle authentication, cookies, or token discovery.
        Can be overridden by subclasses.
        """
        pass

    def crawl(self, context: CrawlerContext) -> Any:
        """
        Extract raw elements or data from the DOM or API.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement crawl()")

    def parse(self, raw_data: Any) -> list:
        """
        Extract structured text from raw elements.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement parse()")

    def normalize(self, parsed_data: list) -> List['JobNormalizedDTO']:
        """
        Standardize data to the schema (handle nulls, compute missing fields).
        Temporarily allows backward compatibility for adapters that return DTOs directly from parse().
        """
        import logging
        import sys
        import os
        # Need to import enrich_skills_from_text from backend
        backend_utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend", "src", "services"))
        if backend_utils_path not in sys.path:
            sys.path.append(backend_utils_path)
        try:
            from skill_enricher import enrich_skills_from_text
        except ImportError:
            def enrich_skills_from_text(t): return []
            
        logger = logging.getLogger(__name__)
        
        normalized = []
        for item in parsed_data:
            if isinstance(item, JobNormalizedDTO):
                if not getattr(item, 'requiredSkills', None):
                    text_for_skills = f"{item.title} {item.description or ''} {item.department or ''}"
                    item.requiredSkills = enrich_skills_from_text(text_for_skills)
                normalized.append(item)
            elif isinstance(item, dict):
                title = item.get("title", "")
                desc = item.get("description", "")
                dept = item.get("department", "")
                
                req_skills = item.get("requiredSkills") or item.get("required_skills") or []
                if not req_skills:
                    text_for_skills = f"{title} {desc} {dept}"
                    req_skills = enrich_skills_from_text(text_for_skills)
                    
                dto = JobNormalizedDTO(
                    companyId=self.company_id,
                    companyName=self.company_name,
                    externalJobId=item.get("externalJobId") or item.get("external_job_id", ""),
                    title=title,
                    description=desc,
                    location=item.get("location"),
                    city=item.get("city"),
                    state=item.get("state"),
                    country=item.get("country"),
                    employmentType=item.get("employmentType"),
                    experience=item.get("experience"),
                    applyUrl=item.get("applyUrl") or item.get("apply_url", ""),
                    sourceATS=item.get("sourceATS", "UNKNOWN"),
                    department=dept,
                    team=item.get("team"),
                    workplaceType=item.get("workplaceType"),
                    publishedAt=item.get("publishedAt"),
                    requiredSkills=req_skills
                )
                normalized.append(dto)
        return normalized

    def submit(self, scraped_jobs: List[JobNormalizedDTO]) -> Dict[str, Any]:
        """
        Core logic to diff against existing database jobs and prepare the payload.
        Do not override unless necessary.
        """
        from src.services.submission_service import SubmissionService
        svc = SubmissionService(self.company)
        return svc.process_and_submit(scraped_jobs)

    def log_execution(self, duration: float):
        """Automatically log execution metrics."""
        print("-" * 40)
        print("CRAWL EXECUTION LOG")
        print(f"Company Name : {self.company_name}")
        print(f"Start Time   : {self.start_time.isoformat()}")
        print(f"End Time     : {self.end_time.isoformat()}")
        print(f"Duration     : {duration:.2f} seconds")
        print(f"Status       : {self.status}")
        if self.error_message:
            print(f"Error        : {self.error_message}")
        print("-" * 40)
