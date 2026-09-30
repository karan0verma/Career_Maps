import time
from playwright.sync_api import sync_playwright

def inspect_99acres_jobs():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
            response = page.goto("https://careers.infoedge.com/infoedge/jobslist", wait_until="networkidle", timeout=30000)
            
            jobs = []
            elements = page.query_selector_all(".job-title") or page.query_selector_all("a[href*='/job/']") or page.query_selector_all("a.title")
            
            for el in elements:
                href = el.get_attribute("href")
                if href:
                    jobs.append((el.inner_text().strip(), href))
                    
            if not jobs:
                print("No direct a tags. Trying to find any links...")
                for l in page.query_selector_all("a"):
                    h = l.get_attribute("href")
                    if h and ('job' in h.lower() or 'detail' in h.lower() or 'view' in h.lower()):
                        print("Link:", l.inner_text().strip(), h)
            
            for t, h in jobs:
                print(f"Job: {t} -> {h}")
                
            browser.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_99acres_jobs()
