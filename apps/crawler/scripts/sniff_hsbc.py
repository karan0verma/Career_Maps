import time
import json
from playwright.sync_api import sync_playwright

def sniff_hsbc():
    print("Sniffing HSBC API...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        def handle_response(response):
            if "graphql" in response.url or "jobs" in response.url or "api" in response.url:
                print(f"API Call: {response.url}")
                try:
                    if response.status == 200:
                        data = response.json()
                        if "jobs" in data or "data" in data:
                            print(f"Found JSON data in {response.url}")
                except:
                    pass
                    
        page.on("response", handle_response)
        page.goto("https://mycareer.hsbc.com/en_GB/external", wait_until="networkidle")
        time.sleep(5)
        # Type "India" in the search box if possible, or just wait
        browser.close()

if __name__ == "__main__":
    sniff_hsbc()
