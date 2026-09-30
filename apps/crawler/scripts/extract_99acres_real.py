import time
from playwright.sync_api import sync_playwright

def inspect_99acres_real():
    print("Following redirect to careers.infoedge.com...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
            response = page.goto("http://careers.infoedge.com/", wait_until="networkidle", timeout=30000)
            print(f"Status: {response.status if response else 'Unknown'}")
            
            print(f"Page title: {page.title()}")
            print(f"Current URL: {page.url}")
            
            job_links = []
            for l in page.query_selector_all("a"):
                href = l.get_attribute("href")
                if href and ('job' in href.lower() or 'apply' in href.lower() or 'career' in href.lower() or 'opening' in href.lower()):
                    job_links.append((l.inner_text().strip(), href))
            
            for t, h in list(set(job_links)):
                print(f"Found: {t} -> {h}")
                
            browser.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_99acres_real()
