import json
import logging
from typing import Dict, Any, List
from src.http_crawler import HttpCrawler
from src.dto.crawler_context import CrawlerContext
from src.dto.job_normalized_dto import JobNormalizedDTO
from src.discovery.response_scorer import ResponseScorer

logger = logging.getLogger(__name__)

class APIExtractor(HttpCrawler):
    def crawl(self, context: CrawlerContext) -> Any:
        config = self.company.get("metadata", {}).get("extraction_config", {})
        api_url = config.get("api_url") or self.company.get("metadata", {}).get("discovered_api_url")
        initial_payload = self.company.get("metadata", {}).get("initial_api_payload")
        
        if not api_url:
            logger.warning(f"[{self.company_name}] No API URL discovered.")
            return []

        jobs_raw = []
        page = 0
        max_pages = 5
        
        # If we have an initial payload from the NetworkInterceptor, use it for page 0
        if initial_payload:
            extracted = self._extract_job_list(initial_payload, config)
            if extracted:
                jobs_raw.extend(extracted)
                page += 1
                
        # Start pagination loop
        while page < max_pages:
            try:
                # Basic pagination query params, potentially overridden by config
                paged_url = self._build_paged_url(api_url, page, config)
                method = config.get("method", "GET").upper()
                
                if method == "GET":
                    response = context.session.get(paged_url, timeout=15)
                else:
                    response = context.session.post(paged_url, timeout=15)
                    
                response.raise_for_status()
                data = response.json()
                
                extracted = self._extract_job_list(data, config)
                if not extracted:
                    break
                    
                jobs_raw.extend(extracted)
                
                if len(extracted) == 0:
                    break
                page += 1
                
            except Exception as e:
                logger.warning(f"[{self.company_name}] Failed to crawl API page {page} at {api_url}: {e}")
                break
                
        return jobs_raw

    def _build_paged_url(self, api_url: str, page: int, config: dict) -> str:
        pagination = config.get("pagination", {})
        if not pagination:
            sep = "&" if "?" in api_url else "?"
            return f"{api_url}{sep}page={page}&offset={page*20}"
            
        p_type = pagination.get("type", "page")
        p_param = pagination.get("parameter", "page")
        p_size = pagination.get("page_size", 20)
        
        val = page if p_type == "page" else page * p_size
        sep = "&" if "?" in api_url else "?"
        
        # If the parameter is already in the URL, replacing it safely requires urllib.parse
        # For simplicity in this engine, we just append it (which usually overrides previous ones in requests)
        return f"{api_url}{sep}{p_param}={val}"

    def _extract_job_list(self, data: Any, config: dict) -> list:
        # 1. Try declarative config first
        if config and config.get("jobs_path"):
            path = config["jobs_path"]
            curr = data
            for p in path.split("."):
                if isinstance(curr, dict) and p in curr:
                    curr = curr[p]
                elif isinstance(curr, list) and p.isdigit():
                    curr = curr[int(p)]
                else:
                    curr = []
                    break
            if isinstance(curr, list):
                return curr
                
        # 2. Fallback to generic scorer
        score, job_list = ResponseScorer.score_response(data)
        if score > 5 and job_list:
            return job_list
        return []

    def parse(self, raw_data: Any) -> list:
        return raw_data if isinstance(raw_data, list) else []
        
    def _get_nested_val(self, item: dict, path: str) -> str:
        curr = item
        for p in path.split("."):
            if isinstance(curr, dict) and p in curr:
                curr = curr[p]
            elif isinstance(curr, list) and p.isdigit() and int(p) < len(curr):
                curr = curr[int(p)]
            else:
                return ""
        return str(curr) if curr is not None else ""

    def _get_val(self, item: Any, keys: list) -> str:
        if not isinstance(item, dict):
            return ""
            
        for k, v in item.items():
            if str(k).lower() in keys:
                if isinstance(v, str):
                    return v
                elif isinstance(v, int):
                    return str(v)
                elif isinstance(v, dict):
                    nested_strs = [str(nv) for nv in v.values() if isinstance(nv, str) or isinstance(nv, int)]
                    if nested_strs:
                        return ", ".join(nested_strs)
        return ""

    def normalize(self, parsed_data: list) -> List[JobNormalizedDTO]:
        normalized = []
        config = self.company.get("metadata", {}).get("extraction_config", {})
        mapping = config.get("field_mapping", {})
        
        for item in parsed_data:
            if not isinstance(item, dict):
                continue
                
            # If declarative mapping exists, use it exclusively
            if mapping:
                title = self._get_nested_val(item, mapping.get("title", ""))
                external_id = self._get_nested_val(item, mapping.get("external_job_id", ""))
                location = self._get_nested_val(item, mapping.get("location", ""))
                description = self._get_nested_val(item, mapping.get("description", ""))
                apply_url = self._get_nested_val(item, mapping.get("apply_url", ""))
            else:
                # Generic fallback
                title = self._get_val(item, ResponseScorer.JOB_SIGNALS['title'])
                external_id = self._get_val(item, ResponseScorer.JOB_SIGNALS['id'])
                location = self._get_val(item, ResponseScorer.JOB_SIGNALS['location'])
                description = self._get_val(item, ResponseScorer.JOB_SIGNALS['description'])
                apply_url = self._get_val(item, ResponseScorer.JOB_SIGNALS['url'])
                
            if not title:
                continue
            
            if not apply_url:
                apply_url = self.career_url
                
            dto = JobNormalizedDTO(
                companyId=self.company_id,
                companyName=self.company_name,
                externalJobId=str(external_id)[:255] if external_id else "",
                title=str(title)[:255],
                description=str(description),
                location=str(location)[:255] if location else "",
                city=None,
                state=None,
                country=None,
                experience=None,
                employmentType=None,
                applyUrl=str(apply_url),
                sourceATS="GENERIC_API"
            )
            normalized.append(dto)
        return normalized
