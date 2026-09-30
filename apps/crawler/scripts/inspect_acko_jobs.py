import time
from playwright.sync_api import sync_playwright

def inspect_acko_jobs():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
            
            def handle_res(response):
                if 'api' in response.url.lower() or 'job' in response.url.lower():
                    if response.status == 200 and 'json' in response.headers.get('content-type', ''):
                        print(f"JSON endpoint: {response.url}")
            
            page.on("response", handle_res)
            
            response = page.goto("https://www.acko.com/careers/jobs/", wait_until="networkidle", timeout=30000)
            print(f"URL: {page.url}")
            
            jobs = []
            for l in page.query_selector_all("a"):
                href = l.get_attribute("href")
                if href and '/careers/jobs/' in href.lower() and len(href) > 20:
                    jobs.append((l.inner_text().strip(), href))
                    
            for t, h in list(set(jobs)):
                print(f"Found Job: {t} -> {h}")
                
            browser.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_acko_jobs()
