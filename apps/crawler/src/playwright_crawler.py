import os
import traceback
from datetime import datetime
from typing import Dict, Any
from playwright.sync_api import sync_playwright, Page
from src.base_crawler import BaseCrawler
from src.dto.crawler_context import CrawlerContext

class PlaywrightCrawler(BaseCrawler):
    def __init__(self, company_data: Dict[str, Any]):
        super().__init__(company_data)
        self.page_timeout = 45000  # 45 seconds
        
        # Ensure screenshot directory exists
        self.screenshot_dir = os.path.join(os.getcwd(), "logs", "screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def _take_screenshot(self, page: Page):
        """Save a Playwright screenshot when a crawl fails."""
        import logging
        logger = logging.getLogger(__name__)
        if os.environ.get("DEBUG_SCREENSHOTS") != "1":
            return None
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = self.company_name.replace(" ", "_").lower()
            screenshot_path = os.path.join(self.screenshot_dir, f"{safe_name}_error_{timestamp}.png")
            page.screenshot(path=screenshot_path, full_page=True)
            logger.info(f"[{self.company_name}] Error screenshot saved to {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.error(f"[{self.company_name}] Failed to capture screenshot: {e}")
            return None

    def execute(self) -> Dict[str, Any]:
        """Main execution loop wrapping Playwright initialization and retry logic."""
        import logging
        import playwright.sync_api
        logger = logging.getLogger(__name__)
        
        self.start_time = datetime.now()
        self.status = "running"
        
        logger.info(f"[{self.company_name}] Starting PlaywrightCrawler for {self.career_url}")
        result_payload = None

        from playwright_stealth import Stealth
        from fake_useragent import UserAgent
        ua = UserAgent()

        with Stealth().use_sync(sync_playwright()) as p:
            for attempt in range(self.max_retries + 1):
                browser = None
                try:
                    # Disable automation features to bypass WAFs
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
                    
                    page.set_default_timeout(self.page_timeout)
                    
                    self.random_delay()
                    
                    # Create the CrawlerContext
                    context = CrawlerContext(page=page)
                    
                    # Execute the plugin pipeline
                    result_payload = self._execute_lifecycle(context)
                    
                    self.status = "SUCCESS"
                    break  # Success, exit retry loop
                    
                except (playwright.sync_api.TimeoutError, playwright.sync_api.Error) as e:
                    self.error_message = str(e)
                    logger.warning(f"[{self.company_name}] Attempt {attempt + 1} failed: {e}")
                    
                    if browser and 'page' in locals() and not page.is_closed():
                        self._take_screenshot(page)
                        
                    if attempt < self.max_retries:
                        logger.info(f"[{self.company_name}] Retrying in a few seconds...")
                        self.random_delay()
                    else:
                        self.status = "FAILED"
                        logger.error(f"[{self.company_name}] Max retries reached.")
                        logger.error(traceback.format_exc())
                except Exception as e:
                    self.error_message = str(e)
                    self.status = "FAILED"
                    logger.error(f"[{self.company_name}] Execution failed (unexpected): {e}")
                    logger.error(traceback.format_exc())
                    break
                finally:
                    if browser:
                        browser.close()

        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        self.log_execution(duration)
        return self._finalize_result(result_payload)
