import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY")
        self.use_mock = not self.api_key

    def _call_real_llm(self, prompt: str) -> str:
        # In a real environment, this would initialize the OpenAI/Gemini SDK
        # and return the string response. 
        raise NotImplementedError("Real LLM call not configured in environment.")

    def generate_schema_mapping(self, domain: str, json_sample: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Takes a domain and a sample JSON structure and returns a declarative mapping.
        Falls back to a deterministic mock for testing if no API key is available.
        """
        logger.info(f"[{domain}] Requesting schema mapping from LLM...")
        
        if not self.use_mock:
            # If we had a real key, we'd prompt the LLM:
            prompt = f"""
            Given this JSON sample from {domain}, output a strict JSON mapping configuration.
            The mapping should define 'jobs_path' (the dot-notation path to the array of jobs),
            and 'field_mapping' containing paths relative to a single job object for:
            'title', 'location', 'description', 'apply_url', 'external_job_id'.
            
            Sample: {json.dumps(json_sample)[:1000]}
            """
            try:
                response = self._call_real_llm(prompt)
                return json.loads(response)
            except Exception as e:
                logger.error(f"LLM call failed: {e}")
                return None
                
        else:
            logger.info(f"[{domain}] No LLM API Key. Using deterministic MOCK LLM mapping.")
            # Deterministic Mocks to prove architecture and cache functionality
            if "apple.com" in domain:
                return {
                    "is_mock": True,
                    "jobs_path": "searchResults",
                    "field_mapping": {
                        "title": "postingTitle",
                        "external_job_id": "positionId",
                        "location": "locations.0.name",
                        "description": "jobSummary",
                        "apply_url": "positionId"
                    },
                    "pagination": {
                        "type": "page",
                        "parameter": "page",
                        "page_size": 20
                    }
                }
            elif "netflix.com" in domain:
                return {
                    "is_mock": True,
                    "jobs_path": "records",
                    "field_mapping": {
                        "title": "text",
                        "external_job_id": "external_id",
                        "location": "location",
                        "description": "description",
                        "apply_url": "url"
                    },
                    "pagination": {
                        "type": "page",
                        "parameter": "page",
                        "page_size": 20
                    }
                }
            return None

    def navigate_spa(self, domain: str, page, interceptor) -> Optional[Dict[str, Any]]:
        """
        Navigates an SPA using the Playwright page. Triggers network interception.
        """
        logger.info(f"[{domain}] Asking LLM to navigate SPA...")
        
        if not self.use_mock:
            # Real LLM Agent loop
            return None
            
        else:
            logger.info(f"[{domain}] No LLM API Key. Using deterministic MOCK Navigation.")
            
            if "apple.com" in domain:
                # Mock Apple's complex search flow
                try:
                    page.goto("https://jobs.apple.com/en-us/search", wait_until="networkidle")
                    # Wait for the search payload to fire
                    page.wait_for_timeout(3000)
                    
                    if interceptor.best_score >= 10:
                        return {
                            "api_url": interceptor.best_url,
                            "initial_payload": interceptor.best_payload,
                            "method": "GET"
                        }
                except Exception as e:
                    logger.warning(f"Mock Apple navigation failed: {e}")
                    
            elif "netflix.com" in domain:
                # Mock Netflix's complex search flow
                try:
                    page.goto("https://jobs.netflix.com/search", wait_until="networkidle")
                    page.wait_for_timeout(3000)
                    if interceptor.best_score >= 10:
                        return {
                            "api_url": interceptor.best_url,
                            "initial_payload": interceptor.best_payload,
                            "method": "GET"
                        }
                except Exception:
                    pass
                    
            return None
