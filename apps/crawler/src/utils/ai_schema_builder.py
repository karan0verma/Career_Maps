import os
import json
import logging
import requests

logger = logging.getLogger(__name__)

class AISchemaBuilder:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        
    def generate_schema(self, evidence: dict) -> dict:
        """
        evidence can contain 'html', 'json_responses', etc.
        Returns a dict with 'jobs' (the actual extracted jobs) and 'config' (the deterministic extraction config).
        """
        if not self.api_key:
            logger.error("GEMINI_API_KEY not found in environment.")
            return {"jobs": [], "config": {}}
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        
        prompt = """
        You are a highly advanced web scraping AI. I will provide you with either an HTML payload or a JSON payload captured from a company's career website.
        
        Your task is to:
        1. Extract the actual job listings present in the data.
        2. Generate a deterministic extraction configuration (CSS selectors for HTML, or JSON paths for JSON) so that future crawls can extract the jobs without using an LLM.
        
        Output MUST be strict JSON in this exact format, with no markdown formatting or extra text:
        {
            "jobs": [
                {
                    "title": "Software Engineer",
                    "location": "New York",
                    "url": "https://example.com/job/123",
                    "job_id": "123",
                    "description": "Optional brief snippet"
                }
            ],
            "config": {
                "source_type": "DOM", // or "API"
                "job_selector": ".job-card-class", // CSS selector for the job container (or JSON array path if API)
                "title_selector": "h3.title", // Relative CSS selector from job_selector (or relative JSON key)
                "location_selector": ".loc",
                "url_selector": "a.apply-link"
            }
        }
        """
        
        # Keep evidence small to avoid token limits
        html = evidence.get("html", "")[:200000] if evidence.get("html") else ""
        jsons = json.dumps(evidence.get("json_responses", []))[:100000]
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt + f"\n\nHTML:\n{html}\n\nJSON Data:\n{jsons}"}]
            }]
        }
        
        try:
            resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
            resp.raise_for_status()
            
            data = resp.json()
            text_response = data['candidates'][0]['content']['parts'][0]['text']
            
            # clean markdown
            if text_response.startswith("```json"):
                text_response = text_response.replace("```json", "", 1).strip()
            if text_response.endswith("```"):
                text_response = text_response[:-3].strip()
                
            return json.loads(text_response)
        except Exception as e:
            logger.error(f"Failed to generate schema via LLM: {e}")
            return {"jobs": [], "config": {}}
