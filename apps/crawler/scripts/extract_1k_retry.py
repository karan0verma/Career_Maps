import time
from playwright.sync_api import sync_playwright

def inspect_1k_kirana():
    print("Retrying 1K Kirana with ignore_https_errors=True...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
            response = page.goto("https://www.1knetworks.com/careers", wait_until="networkidle", timeout=30000)
            print(f"Status: {response.status if response else 'Unknown'}")
            
            job_links = []
            for l in page.query_selector_all("a"):
                href = l.get_attribute("href")
                if href and ('job' in href.lower() or 'apply' in href.lower() or 'career' in href.lower()):
                    job_links.append((l.inner_text().strip(), href))
            
            if not job_links:
                print("No direct job links found. Checking if page has an iframe or ATS redirect...")
                print("Page title:", page.title())
            
            for t, h in job_links:
                print(f"Found: {t} -> {h}")
                
            browser.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_1k_kirana()
