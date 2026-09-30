import time
from playwright.sync_api import sync_playwright

def inspect_acko():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
            response = page.goto("https://www.acko.com/careers", wait_until="networkidle", timeout=30000)
            print(f"Status: {response.status if response else 'Unknown'}")
            print(f"URL: {page.url}")
            
            jobs = []
            for l in page.query_selector_all("a"):
                href = l.get_attribute("href")
                if href and ('job' in href.lower() or 'apply' in href.lower() or 'career' in href.lower() or 'openings' in href.lower() or 'lever' in href.lower() or 'greenhouse' in href.lower() or 'workday' in href.lower()):
                    jobs.append((l.inner_text().strip(), href))
                    
            for t, h in list(set(jobs)):
                print(f"Found: {t} -> {h}")
                
            browser.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_acko()
