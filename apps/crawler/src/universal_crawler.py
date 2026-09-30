import logging
import json
from typing import Dict, Any, List
from urllib.parse import urlparse
from src.playwright_crawler import PlaywrightCrawler
from src.dto.crawler_context import CrawlerContext
from src.dto.job_normalized_dto import JobNormalizedDTO
from src.discovery.response_scorer import ResponseScorer
from src.extractors.api_extractor import APIExtractor
from src.extractors.generic_dom_extractor import GenericDOMExtractor

logger = logging.getLogger(__name__)

class UniversalCrawler(PlaywrightCrawler):
    def __init__(self, company_data: Dict[str, Any]):
        super().__init__(company_data)
        self.captured_apis = []
        
    def _score_dom_job(self, job: dict, url: str) -> float:
        score = 0
        
        # 1. Title presence
        title = job.get('title', '').strip()
        if title:
            score += 2
            
        # 2. URL presence and job-like
        apply_url = job.get('applyUrl', '')
        if apply_url:
            score += 2
            if any(kw in apply_url.lower() for kw in ['job', 'career', 'req', 'position', 'role', 'apply']):
                score += 2
                
            # Must not be the same as the base URL exactly
            if apply_url == url or apply_url == url + '/':
                score -= 5
                
        # 3. Text length (too long is probably a paragraph, too short is probably a nav link)
        if 5 < len(title) < 100:
            score += 1
            
        return score

    def _extract_from_dom(self, page, url: str) -> List[dict]:
        # Auto-pagination / Load More heuristic
        for _ in range(20):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            
            # Look for Next / Load More buttons and click them if found
            clicked = page.evaluate("""
                () => {
                    const buttons = Array.from(document.querySelectorAll('a, button'));
                    for (let b of buttons) {
                        let text = (b.innerText || '').toLowerCase();
                        if ((text.includes('load more') || text.includes('next') || text === '>') && b.offsetParent !== null) {
                            b.click();
                            return true;
                        }
                    }
                    return false;
                }
            """)
            if not clicked:
                break
            page.wait_for_timeout(3000)
            
        elements_data = page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a'));
                return links.map(a => {
                    // Try to get title from nearby headings or parent container
                    let title = a.innerText.trim();
                    let parent = a.parentElement;
                    while (parent && parent.innerText && parent.innerText.length < 200 && parent !== document.body) {
                        let text = parent.innerText.trim();
                        if (text.length > title.length) {
                            title = text;
                        }
                        parent = parent.parentElement;
                    }
                    // Clean up title (remove newlines)
                    title = title.replace(/\\n/g, ' - ').replace(/\\s+/g, ' ');
                    return {
                        text: title,
                        href: a.href,
                        id: a.id || '',
                        className: a.className || ''
                    };
                });
            }
        """)
        
        raw_jobs = []
        seen = set()
        for item in elements_data:
            if not item['href'] or item['href'] in seen:
                continue
            seen.add(item['href'])
            raw_jobs.append({
                "title": item['text'],
                "applyUrl": item['href']
            })
            
        high_confidence_jobs = []
        for j in raw_jobs:
            confidence = self._score_dom_job(j, url)
            j['confidence'] = confidence
            if confidence >= 5:
                high_confidence_jobs.append(j)
                
        return high_confidence_jobs

    def crawl(self, context: CrawlerContext) -> Any:
        page = context.page
        scorer = ResponseScorer()
        
        def handle_response(response):
            try:
                if "application/json" in response.headers.get("content-type", ""):
                    payload = response.json()
                    score = scorer.score_response(payload)
                    if score > 5:
                        self.captured_apis.append({
                            "url": response.url,
                            "method": response.request.method,
                            "payload": payload,
                            "score": score
                        })
            except:
                pass
                
        page.on("response", handle_response)
        
        logger.info(f"[{self.company_name}] UniversalCrawler navigating to {self.career_url}")
        
        try:
            page.goto(self.career_url, wait_until="networkidle", timeout=self.page_timeout)
        except Exception as e:
            logger.warning(f"[{self.company_name}] Navigation error: {e}")
            
        # Give JS time to fetch APIs
        page.wait_for_timeout(3000)
        
        # 1. Evaluate Captured APIs
        if self.captured_apis:
            # sort by highest score
            best_api = sorted(self.captured_apis, key=lambda x: x['score'], reverse=True)[0]
            logger.info(f"[{self.company_name}] Discovered High-Confidence API: {best_api['url']}")
            
            # Use logic similar to APIExtractor to map it
            raw_data = best_api['payload']
            if isinstance(raw_data, dict):
                for k, v in raw_data.items():
                    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                        raw_data = v
                        break
                        
            if not isinstance(raw_data, list):
                raw_data = [raw_data]
                
            self.company["metadata"] = self.company.get("metadata", {})
            self.company["metadata"]["extraction_config"] = {
                "source_type": "API",
                "api_url": best_api['url'],
                "method": best_api['method']
            }
            self._extraction_strategy = "UNIVERSAL_API"
            return raw_data
            
        # 2. Fallback to DOM Extraction
        logger.info(f"[{self.company_name}] No API found. Falling back to DOM Extraction.")
        high_conf_jobs = self._extract_from_dom(page, self.career_url)
        
        self.company["metadata"] = self.company.get("metadata", {})
        self.company["metadata"]["extraction_config"] = {
            "source_type": "DOM"
        }
        self._extraction_strategy = "UNIVERSAL_DOM"
        return high_conf_jobs

    def parse(self, raw_data: Any) -> list:
        # Data is already parsed into lists by crawl
        return raw_data if isinstance(raw_data, list) else []

    def normalize(self, parsed_data: list) -> List[JobNormalizedDTO]:
        normalized = []
        strategy = getattr(self, "_extraction_strategy", "UNIVERSAL_DOM")
        
        if strategy == "UNIVERSAL_API":
            extractor = APIExtractor(self.company)
            # We don't have explicit field mappings from LLM, so we rely on Generic API fallback
            return extractor.normalize(parsed_data)
            
        else:
            extractor = GenericDOMExtractor(self.company)
            return extractor.normalize(parsed_data)
