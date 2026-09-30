from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Navigating to Amazon jobs...")
        page.goto("https://amazon.jobs/en/search", wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        
        print(f"Page title: {page.title()}")
        
        body = page.inner_html("body")
        print(f"Body length: {len(body)}")
        
        if "Request blocked" in body or "CAPTCHA" in body or "Robot" in page.title() or "Access Denied" in page.title():
            print("Blocked by anti-bot.")
        else:
            import re
            jobs = page.query_selector_all(".job-tile, .job-card, [class*='job']")
            print(f"Found {len(jobs)} elements that might be job cards.")
            if not jobs:
                print(body[:2000])
            for job in jobs[:2]:
                print("Job card HTML snippet:")
                print(job.inner_html()[:500])

        browser.close()

if __name__ == "__main__":
    run()
