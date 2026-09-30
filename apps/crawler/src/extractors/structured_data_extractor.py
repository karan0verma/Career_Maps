import json
import logging
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from src.http_crawler import HttpCrawler
from src.dto.crawler_context import CrawlerContext
from src.dto.job_normalized_dto import JobNormalizedDTO

logger = logging.getLogger(__name__)

class StructuredDataExtractor(HttpCrawler):
    def crawl(self, context: CrawlerContext) -> Any:
        response = context.session.get(self.career_url, timeout=15)
        response.raise_for_status()
        return response.text

    def parse(self, raw_data: Any) -> list:
        soup = BeautifulSoup(raw_data, 'html.parser')
        scripts = soup.find_all('script', type='application/ld+json')
        
        job_postings = []
        for script in scripts:
            try:
                data = json.loads(script.string)
                self._extract_job_postings(data, job_postings)
            except Exception as e:
                logger.warning(f"[{self.company_name}] Failed to parse JSON-LD block: {e}")
                
        return job_postings

    def _extract_job_postings(self, data: Any, result: list):
        if isinstance(data, dict):
            # Check if this is a JobPosting or contains one
            obj_type = data.get('@type', '')
            if obj_type == 'JobPosting' or (isinstance(obj_type, list) and 'JobPosting' in obj_type):
                result.append(data)
            elif '@graph' in data:
                self._extract_job_postings(data['@graph'], result)
            else:
                # Recursively check other dictionary values
                for v in data.values():
                    if isinstance(v, (dict, list)):
                        self._extract_job_postings(v, result)
        elif isinstance(data, list):
            for item in data:
                self._extract_job_postings(item, result)

    def normalize(self, parsed_data: list) -> List[JobNormalizedDTO]:
        normalized = []
        for item in parsed_data:
            title = item.get('title', '')
            if not title:
                continue
                
            description = item.get('description', '')
            
            # Extract Location
            location_str = ""
            loc_data = item.get('jobLocation', {})
            if isinstance(loc_data, list) and len(loc_data) > 0:
                loc_data = loc_data[0]
            if isinstance(loc_data, dict):
                address = loc_data.get('address', {})
                if isinstance(address, dict):
                    parts = []
                    for k in ['addressLocality', 'addressRegion', 'addressCountry']:
                        val = address.get(k)
                        if val and isinstance(val, str):
                            parts.append(val)
                    location_str = ", ".join(parts)
            
            # Extract Identifier
            identifier = ""
            id_data = item.get('identifier', {})
            if isinstance(id_data, dict):
                identifier = id_data.get('value', '')
            elif isinstance(id_data, str):
                identifier = id_data
                
            # Extract URL
            apply_url = item.get('url', '')
            if not apply_url:
                apply_url = self.career_url # Fallback if URL is missing
                
            published_at = item.get('datePosted', '')
            employment_type = item.get('employmentType', '')
            if isinstance(employment_type, list):
                employment_type = employment_type[0] if employment_type else ''
                
            dto = JobNormalizedDTO(
                companyId=self.company_id,
                companyName=self.company_name,
                externalJobId=str(identifier) if identifier else "",
                title=str(title),
                description=str(description),
                location=str(location_str),
                city=None,
                state=None,
                country=None,
                experience=None,
                employmentType=str(employment_type) if employment_type else None,
                applyUrl=str(apply_url),
                sourceATS="JSON_LD",
                publishedAt=str(published_at) if published_at else None
            )
            normalized.append(dto)
            
        return normalized
