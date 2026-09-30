from playwright.sync_api import sync_playwright

def dump_tm():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://careers.techmahindra.com/CurrentOpportunity.aspx", wait_until="networkidle")
        
        # See what elements have 'JobDetails.aspx' or similar
        content = page.content()
        import re
        job_ids = re.findall(r'JobId=\d+', content)
        print("Found Job IDs:", list(set(job_ids)))
        
        browser.close()

if __name__ == "__main__":
    dump_tm()
