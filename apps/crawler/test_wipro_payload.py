import json
import time
from playwright.sync_api import sync_playwright

urls = [
    ("Wipro", "https://careers.wipro.com/careers-home/jobs?page=1")
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for name, url in urls:
        print(f"Inspecting {name}...")
        context = browser.new_context()
        page = context.new_page()
        
        def handle_response(response):
            if response.request.resource_type in ["fetch", "xhr"]:
                url = response.url
                if "google-analytics" not in url and "demdex" not in url and "onetrust" not in url:
                    try:
                        text = response.text()
                        if "job" in text.lower():
                            print(f"Found jobs in: {url}")
                            print(text[:200])
                    except:
                        pass
                    
        page.on("response", handle_response)
        
        try:
            page.goto(url, wait_until="networkidle", timeout=45000)
            time.sleep(10)
        except Exception as e:
            print(f"Error loading {name}: {e}")
            
        context.close()
    
    browser.close()
