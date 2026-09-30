import json
import time
from playwright.sync_api import sync_playwright

urls = [
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
                # Ignore analytics and tracking
                if "google-analytics" not in url and "demdex" not in url and "onetrust" not in url:
                    apis.append(url)
                    
        page.on("response", handle_response)
        
        try:
            page.goto(url, wait_until="networkidle", timeout=45000)
            time.sleep(10)
        except Exception as e:
            print(f"Error loading {name}: {e}")
            
        results[name] = apis
        context.close()
    
    browser.close()

with open("wipro_successfactors.json", "w") as f:
    json.dump(results, f, indent=2)
print("Saved to wipro_successfactors.json")
