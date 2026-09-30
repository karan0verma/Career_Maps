import logging
import json
from typing import Dict, Any, Tuple
from playwright.sync_api import sync_playwright

from .response_scorer import ResponseScorer

logger = logging.getLogger(__name__)

class NetworkInterceptor:
    """
    Intercepts and analyzes XHR/Fetch network requests in Playwright 
    to discover underlying API endpoints.
    """
    def __init__(self, career_url: str):
        self.career_url = career_url
        self.best_score = 0
        self.best_url = None
        self.best_payload = None

    def intercept_and_score(self) -> Tuple[str, Any]:
        """
        Loads the career page and intercepts all responses.
        Returns the best API URL and its JSON payload if score > threshold.
        """
        logger.info(f"Starting NetworkInterceptor for {self.career_url}")
        
        try:
            from playwright_stealth import Stealth
            from fake_useragent import UserAgent
            ua = UserAgent()

            with Stealth().use_sync(sync_playwright()) as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--disable-infobars",
                        "--no-sandbox",
                        "--disable-setuid-sandbox"
                    ]
                )
                browser_context = browser.new_context(
                    user_agent=ua.random,
                    viewport={"width": 1920, "height": 1080}
                )
                page = browser_context.new_page()
                
                # Setup network interception
                page.on("response", self._handle_response)
                
                # Navigate and wait for network to settle
                page.goto(self.career_url, wait_until="networkidle", timeout=20000)
                
                # Sometimes SPAs load data a bit later
                page.wait_for_timeout(3000)
                
                browser.close()
                
        except Exception as e:
            logger.warning(f"NetworkInterceptor Playwright execution failed: {e}")
            
        if self.best_score >= 10:  # Threshold for strong job signal
            logger.info(f"NetworkInterceptor found strong API ({self.best_score}): {self.best_url}")
            return self.best_url, self.best_payload
            
        logger.info(f"NetworkInterceptor found no strong APIs. Best score was {self.best_score}")
        return None, None
        
    def _handle_response(self, response):
        # Ignore preflights or non-successful requests
        if response.status >= 400 or response.request.method == "OPTIONS":
            return
            
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return
            
        url = response.url
        # Ignore obvious tracking/asset URLs to save parsing time
        ignore_kws = ["analytics", "tracking", "telemetry", "google", "facebook", "fonts", "css"]
        if any(kw in url.lower() for kw in ignore_kws):
            return
            
        try:
            body = response.json()
            score, job_list = ResponseScorer.score_response(body)
            
            if score > self.best_score:
                self.best_score = score
                self.best_url = url
                self.best_payload = body
                logger.debug(f"New best API candidate found: {url} (Score: {score})")
                
        except Exception as e:
            # Body might not be valid JSON or might be too large
            pass
