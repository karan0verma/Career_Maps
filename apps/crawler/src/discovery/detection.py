import os
import yaml
import requests
import logging
import re
from .models import Target
from .pipeline import PipelineStage

logger = logging.getLogger(__name__)

class StrategySelector(PipelineStage):
    def __init__(self, config_path: str = None):
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), "signatures.yaml")
            
        with open(config_path, 'r', encoding='utf-8') as f:
            self.signatures = yaml.safe_load(f)
            
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

    def _generate_slugs(self, domain: str) -> list:
        slugs = []
        base = domain.lower().split(".")[0]
        slugs.append(base)
        
        clean_base = re.sub(r'[^a-z0-9]', '', base)
        if clean_base != base:
            slugs.append(clean_base)
            
        slugs.extend([f"{clean_base}inc", f"{clean_base}llc", f"{clean_base}corp", f"join{clean_base}"])
        
        unique_slugs = []
        for s in slugs:
            if s not in unique_slugs and len(s) >= 3:
                unique_slugs.append(s)
        return unique_slugs[:5]

    def _probe_direct_apis(self, domain: str) -> tuple[str, str]:
        slugs = self._generate_slugs(domain)
        logger.debug(f"[{domain}] Probing direct APIs with slugs: {slugs}")
        
        for slug in slugs:
            try:
                r = self.session.get(f"https://boards-api.greenhouse.io/v1/boards/{slug}", timeout=3)
                if r.status_code == 200:
                    data = r.json()
                    board_name = data.get("name", "").lower()
                    domain_base = domain.split(".")[0].lower()
                    if domain_base in board_name or slug in board_name:
                        return ("GREENHOUSE", slug)
            except Exception:
                pass
                
            try:
                r = self.session.get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}", timeout=3)
                if r.status_code == 200:
                    return ("ASHBY", slug)
            except Exception:
                pass
                
            try:
                r = self.session.get(f"https://api.lever.co/v0/postings/{slug}", timeout=3)
                if r.status_code == 200:
                    return ("LEVER", slug)
            except Exception:
                pass
                
            try:
                r = self.session.get(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings", timeout=3)
                if r.status_code == 200 and r.json().get("totalFound", 0) > 0:
                    return ("SMARTRECRUITERS", slug)
            except Exception:
                pass
                
            for node in ["wd1", "wd3", "wd5", "wd12"]:
                try:
                    url = f"https://{slug}.{node}.myworkdayjobs.com/{slug.capitalize()}"
                    r = self.session.head(url, timeout=3, allow_redirects=True)
                    if r.status_code == 200:
                        return ("WORKDAY", f"{slug}:{node}")
                except Exception:
                    pass
        return (None, None)

    def process(self, target: Target) -> Target:
        if not target.career_url or target.extraction_strategy:
            return target
            
        logger.info(f"[{target.domain}] Running StrategySelector on {target.career_url}...")
        
        # 1. URL pattern matching (Known ATS)
        for ats_key, rules in self.signatures.items():
            if 'url' in rules:
                for pattern in rules['url']:
                    if pattern in target.career_url.lower():
                        target.ats_type = ats_key
                        target.extraction_strategy = "KNOWN_ATS"
                        target.detection_confidence = 1.0
                        logger.info(f"[{target.domain}] Strategy Selected: KNOWN_ATS ({ats_key}) via URL")
                        return target
                        
        # 2. Direct ATS API Probing
        probed_ats, slug = self._probe_direct_apis(target.domain)
        if probed_ats:
            target.ats_type = probed_ats
            target.extraction_strategy = "KNOWN_ATS"
            target.detection_confidence = 0.85
            if slug:
                target.metadata["board_token"] = slug
            logger.info(f"[{target.domain}] Strategy Selected: KNOWN_ATS ({probed_ats}) via Direct API Probing")
            return target
            
        # 3. HTML body matching (Known ATS or JSON-LD)
        try:
            resp = self.session.get(target.career_url, timeout=10)
            html_content = resp.text
            
            for ats_key, rules in self.signatures.items():
                if 'html' in rules:
                    for pattern in rules['html']:
                        if pattern in html_content:
                            target.ats_type = ats_key
                            target.extraction_strategy = "KNOWN_ATS"
                            target.detection_confidence = 0.9
                            logger.info(f"[{target.domain}] Strategy Selected: KNOWN_ATS ({ats_key}) via HTML")
                            return target
                            
            if '"@type": "JobPosting"' in html_content or '"@type":"JobPosting"' in html_content:
                target.extraction_strategy = "STRUCTURED_JSON_LD"
                target.detection_confidence = 0.9
                logger.info(f"[{target.domain}] Strategy Selected: STRUCTURED_JSON_LD")
                return target
                
        except requests.RequestException as e:
            logger.warning(f"[{target.domain}] Error fetching HTML for strategy selection: {e}")
            
        # 4. SPA Fallback & Network Request Scanning (NetworkInterceptor)
        logger.info(f"[{target.domain}] Static checks failed. Falling back to NetworkInterceptor...")
        try:
            from .network_interceptor import NetworkInterceptor
            interceptor = NetworkInterceptor(target.career_url)
            api_url, api_payload = interceptor.intercept_and_score()
            
            # If standard interception fails, try LLM Navigation Agent
            if not api_url:
                logger.info(f"[{target.domain}] Standard intercept failed. Invoking LLM Navigation Agent...")
                from src.agents.llm_client import LLMClient
                from playwright.sync_api import sync_playwright
                
                llm = LLMClient()
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    # Hook the same interceptor up to the new page
                    page.on("response", interceptor._handle_response)
                    
                    llm_result = llm.navigate_spa(target.domain, page, interceptor)
                    if llm_result and llm_result.get("api_url"):
                        api_url = llm_result["api_url"]
                        api_payload = llm_result["initial_payload"]
                        target.metadata["llm_nav_used"] = True
                    
                    browser.close()
            
            # If we found an API (either standard or via LLM Nav), try LLM Schema Mapping
            if api_url and api_payload:
                target.extraction_strategy = "GENERIC_API"
                target.detection_confidence = 0.8
                target.metadata['discovered_api_url'] = api_url
                target.metadata['initial_api_payload'] = api_payload
                
                # Attempt to get declarative mapping from LLM
                from src.agents.llm_client import LLMClient
                llm = LLMClient()
                mapping = llm.generate_schema_mapping(target.domain, api_payload)
                
                if mapping:
                    target.metadata['extraction_config'] = mapping
                    target.metadata['extraction_config']['api_url'] = api_url
                    target.metadata['extraction_config']['method'] = "GET"
                    target.metadata["llm_map_used"] = True
                    logger.info(f"[{target.domain}] Strategy Selected: GENERIC_API via {api_url} (with LLM Schema)")
                else:
                    logger.info(f"[{target.domain}] Strategy Selected: GENERIC_API via {api_url} (No Schema Mapping)")
                    
                return target
                
            # If no API found, do we have any known ATS matched by the network URLs?
            target.extraction_strategy = "GENERIC_DOM"
            target.detection_confidence = 0.5
            logger.info(f"[{target.domain}] Strategy Selected: GENERIC_DOM")
            return target
                                
        except Exception as e:
            logger.error(f"[{target.domain}] NetworkInterceptor fallback failed: {e}")
            
        logger.info(f"[{target.domain}] All strategies failed.")
        target.status = "FAILED"
        target.errors.append("No viable extraction strategy found.")
        return target
