import re
import os
import json
import logging
from typing import Optional, Dict
from urllib.parse import urlparse
import requests
from playwright.sync_api import sync_playwright, Error
from .cache import JsonTokenCache, TokenCache

logger = logging.getLogger(__name__)

class TokenDiscoveryService:
    # Use a default cache instance
    _cache: TokenCache = JsonTokenCache()
    
    @classmethod
    def set_cache_backend(cls, cache: TokenCache):
        """Allows injecting a different cache backend (e.g. RedisTokenCache)."""
        cls._cache = cache

    @classmethod
    def resolve_token(cls, ats_type: str, company_url: str, company_name: str) -> Optional[str]:
        """
        Universal ATS board token discovery with caching.
        0. Cache Lookup
        1. URL Parsing
        2. Heuristic fallback
        3. Network Interception (Playwright)
        """
        ats_type = ats_type.upper()
        
        # 0. Cache Lookup
        cached_token = cls._cache.get(ats_type, company_url)
        if cached_token:
            return cached_token
        
        # 1. Direct Extraction from URL
        if ats_type == "GREENHOUSE":
            match = re.search(r'boards\.(?:eu\.)?greenhouse\.io/([^/"\?\#]+)', company_url)
            if match:
                token = match.group(1)
                logger.info(f"Resolved {ats_type} token from URL: {token}")
                cls._cache.set(ats_type, company_url, token)
                return token
        elif ats_type == "LEVER":
            match = re.search(r'jobs\.lever\.co/([^/"\?\#]+)', company_url)
            if match:
                token = match.group(1)
                logger.info(f"Resolved {ats_type} token from URL: {token}")
                cls._cache.set(ats_type, company_url, token)
                return token
        elif ats_type == "ASHBY":
            match = re.search(r'jobs\.ashbyhq\.com/([^/"\?\#]+)', company_url)
            if match:
                token = match.group(1)
                logger.info(f"Resolved {ats_type} token from URL: {token}")
                cls._cache.set(ats_type, company_url, token)
                return token
        elif ats_type == "SMARTRECRUITERS":
            match = re.search(r'careers\.smartrecruiters\.com/([^/"\?\#]+)', company_url)
            if match:
                token = match.group(1)
                logger.info(f"Resolved {ats_type} token from URL: {token}")
                cls._cache.set(ats_type, company_url, token)
                return token
        elif ats_type == "WORKABLE":
            match = re.search(r'apply\.workable\.com/([^/"\?\#]+)', company_url)
            if match:
                token = match.group(1)
                logger.info(f"Resolved {ats_type} token from URL: {token}")
                cls._cache.set(ats_type, company_url, token)
                return token
        elif ats_type == "BAMBOOHR":
            match = re.search(r'([^/"\?\#]+)\.bamboohr\.com', company_url)
            if match:
                token = match.group(1)
                logger.info(f"Resolved {ats_type} token from URL: {token}")
                cls._cache.set(ats_type, company_url, token)
                return token
                
        # 1.5 HTML DOM based Extraction
        if ats_type == "JOBVITE":
            # Jobvite uses a custom hash like 'qyV9VfwP', which requires fetching the company's careers page
            # and looking for the CompanyJobs/Xml.aspx?c= token or an iframe src.
            logger.info(f"Attempting HTML-based token extraction for {ats_type} at {company_url}")
            try:
                resp = requests.get(company_url, timeout=10)
                if resp.status_code == 200:
                    from src.services.html_parser.service import HtmlParserService
                    
                    # Look for explicit xml link in the dom or iframe src
                    # e.g., src="/CompanyJobs/Careers.aspx?c=qyV9VfwP" or src="...Xml.aspx?c=qyV9VfwP"
                    token = HtmlParserService.regex_search(resp.text, r'[\?&]c=([a-zA-Z0-9]+)')
                    
                    if token:
                        logger.info(f"Resolved {ats_type} token via HTML extraction: {token}")
                        cls._cache.set(ats_type, company_url, token)
                        return token
            except requests.RequestException as e:
                logger.warning(f"Error extracting HTML token for {ats_type}: {e}")
                
        # 2. Heuristic Fallback
        # Often the company name (without spaces) is the exact board token
        fallback_token = company_name.lower().replace(" ", "")
        logger.info(f"Trying heuristic fallback token for {ats_type}: {fallback_token}")
        
        if ats_type == "GREENHOUSE":
            test_url = f"https://boards-api.greenhouse.io/v1/boards/{fallback_token}/jobs"
            try:
                resp = requests.head(test_url, timeout=5)
                if resp.status_code == 200:
                    cls._cache.set(ats_type, company_url, fallback_token)
                    return fallback_token
            except requests.RequestException:
                pass
        elif ats_type == "LEVER":
            test_url = f"https://api.lever.co/v0/postings/{fallback_token}?mode=json"
            try:
                resp = requests.head(test_url, timeout=5)
                if resp.status_code == 200:
                    cls._cache.set(ats_type, company_url, fallback_token)
                    return fallback_token
            except requests.RequestException:
                pass
        elif ats_type == "SMARTRECRUITERS":
            test_url = f"https://api.smartrecruiters.com/v1/companies/{fallback_token}/postings"
            try:
                resp = requests.get(test_url, timeout=5)
                if resp.status_code == 200 and resp.json().get("totalFound", 0) > 0:
                    cls._cache.set(ats_type, company_url, fallback_token)
                    return fallback_token
            except requests.RequestException:
                pass
                
        # 3. Network Interception via Playwright
        logger.info(f"Token not in URL or heuristic. Launching headless browser for {ats_type} interception...")
        token_found = None
        
        with sync_playwright() as p:
            browser = None
            try:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                def handle_request(request):
                    nonlocal token_found
                    if token_found:
                        return
                    
                    if ats_type == "GREENHOUSE":
                        # API calls
                        api_match = re.search(r'boards-api\.(?:eu\.)?greenhouse\.io/v1/boards/([^/"\?]+)', request.url)
                        if api_match:
                            token_found = api_match.group(1)
                            
                        # Embed JS calls
                        embed_match = re.search(r'greenhouse\.io/embed/job_board/js\?for=([^"\'&]+)', request.url)
                        if embed_match:
                            token_found = embed_match.group(1)
                            
                        # Iframe src
                        if request.frame and request.frame.parent_frame is not None:
                            iframe_match = re.search(r'boards\.(?:eu\.)?greenhouse\.io/([^/"\?]+)', request.url)
                            if iframe_match:
                                token_found = iframe_match.group(1)
                                
                    elif ats_type == "LEVER":
                        api_match = re.search(r'api\.lever\.co/v0/postings/([^/"\?]+)', request.url)
                        if api_match:
                            token_found = api_match.group(1)
                            
                        if request.frame and request.frame.parent_frame is not None:
                            iframe_match = re.search(r'jobs\.lever\.co/([^/"\?]+)', request.url)
                            if iframe_match:
                                token_found = iframe_match.group(1)

                page.on("request", handle_request)
                page.goto(company_url, wait_until="networkidle", timeout=30000)
                
                # Double-check raw HTML for embed codes
                if not token_found:
                    html = page.content()
                    if ats_type == "GREENHOUSE":
                        match = re.search(r'greenhouse\.io/embed/job_board/js\?for=([^"\'&]+)', html)
                        if match: token_found = match.group(1)
                        else:
                            iframe_match = re.search(r'boards\.(?:eu\.)?greenhouse\.io/([^/"\?]+)', html)
                            if iframe_match: token_found = iframe_match.group(1)
                    elif ats_type == "LEVER":
                        iframe_match = re.search(r'jobs\.lever\.co/([^/"\?]+)', html)
                        if iframe_match: token_found = iframe_match.group(1)

            except Error as e:
                logger.warning(f"Error intercepting traffic for {company_url}: {e}")
            finally:
                if browser:
                    browser.close()

        if token_found:
            logger.info(f"Resolved token via network interception: {token_found}")
            cls._cache.set(ats_type, company_url, token_found)
        else:
            logger.warning(f"Failed to resolve {ats_type} token.")
            
        return token_found
