import json
import time
from playwright.sync_api import sync_playwright
import re

urls = {
    "Google": "https://careers.google.com/",
    "Microsoft": "https://jobs.careers.microsoft.com/global/en/search",
    "Amazon": "https://amazon.jobs/en/search",
    "TCS": "https://www.tcs.com/careers",
    "Infosys": "https://www.infosys.com/careers.html",
    "Wipro": "https://careers.wipro.com/",
    "Flipkart": "https://www.flipkartcareers.com/",
    "Zomato": "https://www.zomato.com/careers",
    "Swiggy": "https://careers.swiggy.com/",
    "Meta": "https://www.metacareers.com/"
}

results = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for name, url in urls.items():
        print(f"\\n--- Investigating {name} ---")
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        network_urls = []
        js_bundles = []
        api_endpoints = []
        
        def handle_request(route, request):
            req_url = request.url
            network_urls.append(req_url)
            if req_url.endswith('.js'):
                js_bundles.append(req_url)
            if 'api' in req_url or 'graphql' in req_url or 'json' in req_url or '/cxs/' in req_url:
                api_endpoints.append(req_url)
            route.continue_()

        page.route("**/*", handle_request)
        
        try:
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(3) # Let SPA load
            html = page.content()
            
            # Simple heuristic detection
            ats = "UNKNOWN"
            evidence = []
            confidence = 0
            
            html_lower = html.lower()
            all_urls_str = " ".join(network_urls).lower()
            
            if "myworkdayjobs.com" in all_urls_str or "/wday/cxs" in all_urls_str or "workday" in html_lower:
                ats = "WORKDAY"
                confidence = 100
                evidence.append("Found Workday network requests or specific wday/cxs endpoints.")
            elif "greenhouse.io" in all_urls_str or "boards.greenhouse" in html_lower:
                ats = "GREENHOUSE"
                confidence = 100
                evidence.append("Found Greenhouse API endpoints/iframes.")
            elif "successfactors.com" in all_urls_str or "career8.successfactors.com" in all_urls_str or "successfactors" in html_lower:
                ats = "SUCCESSFACTORS"
                confidence = 100
                evidence.append("Found SuccessFactors network requests.")
            elif "icims.com" in all_urls_str:
                ats = "ICIMS"
                confidence = 100
                evidence.append("Found iCIMS iframe or network requests.")
            elif "eightfold" in html_lower or "eightfold.ai" in all_urls_str:
                ats = "EIGHTFOLD"
                confidence = 100
                evidence.append("Found Eightfold API/JS bundles.")
            elif "taleo.net" in all_urls_str:
                ats = "TALEO"
                confidence = 100
                evidence.append("Found Taleo network endpoints.")
            
            if ats == "UNKNOWN":
                evidence.append("No standard ATS footprints found in network or DOM.")
                confidence = 0
            
            results[name] = {
                "ATS": ats,
                "Confidence": confidence,
                "Evidence": evidence,
                "APIs": api_endpoints[:5],
                "HTML_Size": len(html)
            }
            print(f"Result for {name}: {ats} ({confidence}%) - {evidence}")
            
        except Exception as e:
            print(f"Error investigating {name}: {e}")
            results[name] = {
                "ATS": "UNKNOWN",
                "Confidence": 0,
                "Evidence": [f"Connection error or timeout: {str(e)}"],
                "APIs": [],
                "HTML_Size": 0
            }
        
        context.close()
    
    browser.close()

with open("ats_deep_analysis.json", "w") as f:
    json.dump(results, f, indent=2)
