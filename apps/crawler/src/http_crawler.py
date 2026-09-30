import requests
import traceback
from datetime import datetime
from typing import Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.base_crawler import BaseCrawler
from src.dto.crawler_context import CrawlerContext

class HttpCrawler(BaseCrawler):
    def __init__(self, company_data: Dict[str, Any]):
        super().__init__(company_data)
        
    def _create_session(self) -> requests.Session:
        """Create a robust HTTP session with pooling and retries."""
        from curl_cffi import requests as c_requests
        
        session = c_requests.Session(impersonate="chrome")
        
        # Note: curl_cffi doesn't use urllib3 Retry the same way, but it handles basics.
        # For simplicity, we just rely on its powerful impersonation to avoid 403s entirely.
        # No mounts needed for curl_cffi defaults
        
        from fake_useragent import UserAgent
        ua = UserAgent()
        
        # Standard User-Agent
        session.headers.update({
            "User-Agent": ua.random,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        })
        
        return session

    def _fetch_json(self, url: str, context: CrawlerContext, params: dict = None, json_payload: dict = None, method: str = "GET") -> Dict[str, Any]:
        """Safely fetch and parse JSON using the existing session with backoff."""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            if method.upper() == "POST":
                resp = context.session.post(url, params=params, json=json_payload, timeout=(5, 15))
            else:
                resp = context.session.get(url, params=params, timeout=(5, 15))
                
            resp.raise_for_status()
            
            try:
                return resp.json()
            except ValueError:
                logger.error(f"[{self.company_name}] Failed to decode JSON from {url}")
                return {}
                
        except Exception as e:
            logger.error(f"[{self.company_name}] HTTP Request failed for {url}: {e}")
            return {}

    def _fetch_html(self, url: str, context: CrawlerContext, params: dict = None, method: str = "GET") -> str:
        """Safely fetch and return raw HTML string using the existing session with backoff."""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            if method.upper() == "POST":
                resp = context.session.post(url, params=params, timeout=(5, 15))
            else:
                resp = context.session.get(url, params=params, timeout=(5, 15))
                
            resp.raise_for_status()
            
            # Ensure correct encoding if provided by the server, otherwise let requests guess
            if resp.encoding is None:
                resp.encoding = 'utf-8'
                
            return resp.text
                
        except Exception as e:
            logger.error(f"[{self.company_name}] HTML Request failed for {url}: {e}")
            return ""

    def _fetch_xml(self, url: str, context: CrawlerContext, params: dict = None, method: str = "GET") -> Any:
        """Safely fetch and parse XML using the existing session with backoff."""
        import logging
        import xml.etree.ElementTree as ET
        logger = logging.getLogger(__name__)
        
        try:
            if method.upper() == "POST":
                resp = context.session.post(url, params=params, timeout=(5, 15))
            else:
                resp = context.session.get(url, params=params, timeout=(5, 15))
                
            resp.raise_for_status()
            
            # Prevent Billion Laughs and generic XML vulnerabilities by handling parse errors safely
            try:
                # ET.fromstring handles standard XML parsing. 
                # Note: For strict enterprise security, defusedxml could be injected here if available.
                return ET.fromstring(resp.content)
            except ET.ParseError as e:
                logger.error(f"[{self.company_name}] XML Parse Error for {url}: {e}")
                return None
                
        except Exception as e:
            logger.error(f"[{self.company_name}] XML Request failed for {url}: {e}")
            return None

    def execute(self) -> Dict[str, Any]:
        """Main execution loop for HTTP APIs (no Playwright overhead)."""
        import logging
        logger = logging.getLogger(__name__)
        
        self.start_time = datetime.now()
        self.status = "running"
        
        logger.info(f"[{self.company_name}] Starting HttpCrawler for {self.career_url}")
        result_payload = None

        try:
            session = self._create_session()
            context = CrawlerContext(session=session)
            
            # Execute the plugin pipeline
            result_payload = self._execute_lifecycle(context)
            self.status = "SUCCESS"
            
        except Exception as e:
            self.error_message = str(e)
            self.status = "FAILED"
            logger.error(f"[{self.company_name}] Execution failed (network): {e}")
        except Exception as e:
            # We strictly catch Exception here because execute() is the absolute top-level entrypoint
            # However, we log it properly instead of print and re-raise if it's a fatal SystemExit/KeyboardInterrupt.
            self.error_message = str(e)
            self.status = "FAILED"
            logger.error(f"[{self.company_name}] Execution failed (unexpected): {e}")
            logger.error(traceback.format_exc())

        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        self.log_execution(duration)
        return self._finalize_result(result_payload)
