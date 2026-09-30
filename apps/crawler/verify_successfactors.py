import json
import time
from playwright.sync_api import sync_playwright

urls = [
    ("Microsoft", "https://jobs.careers.microsoft.com/global/en/search"),
    ("Wipro", "https://careers.wipro.com/careers-home/jobs")
]

results = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for name, url in urls:
        print(f"Inspecting {name}...")
        context = browser.new_context()
        page = context.new_page()
        
        apis = []
        
        def handle_response(response):
            if response.request.resource_type in ["fetch", "xhr"]:
                url = response.url
                # Filter for likely job search endpoints
                if "search" in url.lower() or "jobs" in url.lower() or "api" in url.lower() or "graphql" in url.lower() or "pcsx" in url.lower():
                    apis.append(url)
                    
        page.on("response", handle_response)
        
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            # Wait a bit for async requests
            time.sleep(5)
        except Exception as e:
            print(f"Error loading {name}: {e}")
            
        results[name] = apis
        context.close()
    
    browser.close()

with open("successfactors_verification.json", "w") as f:
    json.dump(results, f, indent=2)
print("Saved to successfactors_verification.json")
